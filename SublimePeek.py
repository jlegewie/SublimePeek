## Sublime Text 2 Plugin
#  Show quicklook window of selected R function

import sublime
import sublime_plugin
import subprocess
import threading
import re
import os
import json
import urllib2
import distutils.dir_util

## mac os - quicklook
# /usr/bin/qlmanage -p [FILEPATH]

## linux - gloobus-preview
# /usr/bin/gloobus-preview [FILEPATH]

## load settings
settings = sublime.load_settings(u'SublimePeek.sublime-settings')


class SublimePeekCommand(sublime_plugin.TextCommand):
    # supported languages and accessors
    languages = ("Python", "Ruby", "Ruby on Rails", "RSpec", "CSS", "HTML", "JavaScript", "PHP", "R", "Stata")
    accessors = ("python", "python", "python", "python", "identity", "identity", "mapping", "identity", "identity", "mapping")
    # class variables
    lang = ""
    accessor = ""
    path = ""
    filepath = ""

    def run(self, edit):

        # get language
        self.lang = self.get_language()

        # check whether language is supported
        if not self.lang in self.languages:
            return
        # get accessor from settings
        self.accessor = self.accessors[self.languages.index(self.lang)]

        # path for help files
        self.path = sublime.packages_path() + "/SublimePeek-%s-help/" % (self.lang)
        # check whether help files exists unless generated on the fly ("accessor" == "python")
        if not self.accessor == "python":
            if not os.path.exists(self.path):
                # compile help files or exit if compiling fails
                self.get_help_files()
                return
                #if not self.get_help_files(self.lang, self.path):
                #    return

        # get keyword from selection
        keyword = self.get_keyword()

        # exit if no keyword defined and setting:overview is false
        if keyword == ""  and self.accessor == "python" and not settings.get("overview"):
            return

        # use mapping to get correct keyword
        if self.accessor == "mapping":
            # load mapping file
            map = json.load(open(self.path + '/%s-mapping.json' % (self.lang), "r"))
            map_from = [item['from'] for item in map]

            # get keyword from map
            if keyword in map_from:
                # use map to get keyword
                i = map_from.index(keyword)
                keyword = map[i]['to']
            # if keyword not in map, check wether file can be access directly and otherwise compile list for overview
            else:
                if not os.path.isfile(self.path + "%s.html" % (keyword)):
                    if settings.get("overview"):
                        keyword = self.get_list_of_help_topics(map)
                    else:
                        return

        # generate help file using python (language specific)
        if self.accessor == "python":
            keyword = self.create_help_file(keyword)
            if keyword == False:
                return

        # show help file
        if isinstance(keyword, (str, unicode)):
            self.show_help(keyword)
        if isinstance(keyword, list):
            if len(keyword) == 1:
                self.show_help(keyword[0])
            else:
                self.select_help_file(keyword, [])

    def postPeek(self):
        # remove help file if generated on the fly (self.accessor == "python")
        if self.accessor == "python":
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)

    def popenAndCall(self, popenArgs, onExit):
        """
        Runs the given args in a subprocess.Popen, and then calls the function
        onExit when the subprocess completes.
        onExit is a callable object, and args is a list/tuple of args that
        would give to subprocess.Popen.
        Source: http://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
        """
        def runInThread(onExit, popenArgs):
            proc = subprocess.Popen(popenArgs)
            proc.wait()
            onExit()
            return
        thread = threading.Thread(target=runInThread, args=(onExit, popenArgs))
        thread.start()
        # returns immediately after the thread starts
        return thread

    # call quick look to show help file
    def show_help(self, keyword):
        sublime.status_message("SublimePeek: " + keyword)
        # set filepath of help file
        self.filepath = self.path + "%s.html" % (keyword)

        # quick look
        if os.path.isfile(self.filepath):
            sublime.status_message("SublimePeek: Help for '" + keyword + "'")
            args = ['/usr/bin/qlmanage', '-p', self.filepath]
            # qlmanage documentation list
            # http://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man1/qlmanage.1.html
            self.popenAndCall(args, self.postPeek)
            #p = subprocess.Popen(args)
            #p.wait()
        # if no file found, show overview
        else:
            if settings.get("overview") and self.accessor == "identity":
                keyword = self.get_list_of_help_topics()
                self.select_help_file(keyword, [])
            else:
                sublime.status_message("SublimePeek: No help file found for '" + keyword + "'.")

    def create_help_file(self, keyword):
        # set path for help file
        self.path = sublime.packages_path() + "/SublimePeek/"

        # define arguments for subprocess call
        calls = {
            'Python': ['pydoc', '-w'],
            'Ruby': ['ri', '--format', 'html', '--system', '--gems']
        }

        # select help file to create
        def select_keyword(keywords):
            def callback(index):
                if index != -1:
                    keyword = keywords[index]
                    # get selected help file
                    args = calls[self.lang] + [keyword]
                    output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
                    # save selected help files
                    if self.lang == 'Ruby':
                        write_html_file('ruby', keyword, output, 'ruby')
                        keyword = 'ruby'
                    # show help file
                    self.show_help(keyword)

            # show quick panel for selection of help file
            self.view.window().show_quick_panel(keywords, callback)

        def write_html_file(filename, keyword, content, lang):
            html_page = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="chrome=1"><title>SublimePeek | Help for %s</title><link href="css/%s.css" rel="stylesheet"></head><body><div style="display: block; "><div class="page-header"><h1>%s</h2><!--CONTENT-->%s</div></div></body></html>'
            f = open(self.path + filename + ".html", "w")
            f.write(html_page % (keyword, lang, keyword, content))
            f.close()

        # generate python help file
        if self.lang == "Python":
            # set working dir
            os.chdir(self.path)
            # call pydoc to generate help file in html
            args = calls[self.lang] + [keyword]
            # overview topics: help('keywords'), help('modules'), help('topics')
            output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
            # p = subprocess.Popen(args)
            # p.wait()

            # try to call pydoc again without '-w' argument
            # python bug: http://stackoverflow.com/a/10333615/1318686
            if 'no Python documentation found for' in output:
                output = subprocess.Popen(['pydoc', keyword], stdout=subprocess.PIPE).communicate()[0]
                # exit if no help found
                if 'no Python documentation found for' in output:
                    return keyword
                # write html file
                output = output.replace('\n', '<br>').replace(' ', '&nbsp;')
                write_html_file(keyword, keyword, output, 'python')

            return keyword

        # generate rubin help file
        if self.lang == "Ruby":
            # get help for keyword
            args = calls[self.lang] + [keyword]
            output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
            # exit if no help found
            if output == '':
                return keyword
            # more than one match for keyword
            if "More than one method matched your request." in output:
                output = output.replace("\n", "").replace(" ", "")
                keywords = output.split("mationononeof:")[1].split(",")

                # show quick panel for selection of help file
                select_keyword(keywords)
                return False

            # save file if only one match
            else:
                # save selected help files
                write_html_file('ruby', keyword, output, 'ruby')
                keyword = "ruby"
                return keyword

    def get_language(self):
        # get language file
        lang_file = self.view.settings().get('syntax')
        lang = lang_file.split('/')
        lang = lang[len(lang) - 1].split('.')[0]
        # support common CSS preprocessors
        if lang in ["LESS", "SASS", "SCSS"]:
            lang = "CSS"
        # support common Ruby syntax
        if lang in ["Ruby", "Ruby on Rails", "RSpec"]:
            lang = "Ruby"
        # get scope for embedded PHP, JS, or CSS
        if lang == "HTML":
            scope = self.view.syntax_name(self.view.sel()[0].b)
            if "source.php.embedded.block.html" in scope:
                lang = "PHP"
            if "source.js.embedded.html" in scope:
                lang = "JavaScript"
            if "source.css.embedded.html" in scope:
                lang = "CSS"
        # return language
        return lang

    def get_keyword(self):
        # get selection
        s = self.view.sel()[0]
        pos = s.b
        if s.empty():
            # if cursor at end of line, before " ", or after (, return help for function before (
            if self.view.substr(pos) in ["\n", " "] or self.view.substr(pos - 1) == "(":
                s_str = self.get_word(self.view, pos - 1)
            else:
                s_str = self.get_word(self.view, pos)
        else:
            s_str = self.view.substr(s)

        # get keyword
        sep = re.compile('[\(, ]')
        keyword = sep.split(s_str)[0]
        return keyword

    # use ST2 show_quick_panel to let the user select a help files from a list of functions (e.g. methods for different classes such as String.length and Array.length)
    def select_help_file(self, options, description):
        def on_done(index):
            if index != -1:
                self.show_help(options[index])
        # get list with option and description
        if len(description) == len(options):
            items = []
            for k, op in enumerate(options):
                items.append([op, description[k]])
        else:
            items = options

        # show quick panel for selection of help file
        self.view.window().show_quick_panel(items, on_done)

    def get_list_of_help_topics(self, map=""):
        keyword = []
        # get keywords from mapping file
        if map != "":
            map_to = [item['to'] for item in map]
            for obj in map_to:
                keyword.append(obj[0])
        # get keywords from files in folder
        files = os.listdir(self.path)
        for f, file in enumerate(files):
            if ".html" in file:
                keyword.append(file.replace(".html", ""))
        # clean list (remove dupicates and sort)
        keyword = sorted(list(set(keyword)))
        # return list of keywords
        return keyword

    # adopted from 'expand_word' in default/delete_word.py
    # modifed to get whole word to right and left of pos
    def get_word(self, view, pos):
        ws = ["\t", " "]

        # get word to right of cursor
        delta = 1
        classes = sublime.CLASS_WORD_END | sublime.CLASS_PUNCTUATION_END | sublime.CLASS_LINE_START
        if view.substr(pos) in ws and view.substr(pos + 1) in ws:
            classes = sublime.CLASS_WORD_START | sublime.CLASS_PUNCTUATION_START | sublime.CLASS_LINE_END
        forward = sublime.Region(pos, self.find_by_class(pos + delta, classes, True))

        # get word to left of cursor
        delta = -1
        classes = sublime.CLASS_WORD_START | sublime.CLASS_PUNCTUATION_START | sublime.CLASS_LINE_END
        if view.substr(pos - 1) in ws and view.substr(pos - 2) in ws:
            classes = sublime.CLASS_WORD_END | sublime.CLASS_PUNCTUATION_END | sublime.CLASS_LINE_START
        backward = sublime.Region(pos, self.find_by_class(pos + delta, classes, False))

        # return string of whole word
        return self.view.substr(backward) + self.view.substr(forward)

    # function from default/delete_word.py
    def find_by_class(self, pt, classes, forward):
        if forward:
            delta = 1
            end_position = self.view.size()
            if pt > end_position:
                pt = end_position
        else:
            delta = -1
            end_position = 0
            if pt < end_position:
                pt = end_position

        while pt != end_position:
            if self.view.classify(pt) & classes != 0:
                return pt
            pt += delta

        return pt

    # download and compile help files from DocHub
    # the threading code was adopted from
    # http://net.tutsplus.com/tutorials/python-tutorials/how-to-create-a-sublime-text-2-plugin/
    def get_help_files(self):
        # prompt user (only for version >= 2187)
        # (sublime.ok_cancel_dialog was added in nightly 2187)
        if sublime.version() >= 2187:
            if not sublime.ok_cancel_dialog("SublimePeek\nDo you want to download and compile the help files for '%s'?" % (self.lang)):
                sublime.status_message("SublimePeek: Help files for '%s' are not installed." % (self.lang))
                return
        # start download thread
        threads = []
        thread = GetHelpFiles(self.lang, self.path, 5)
        threads.append(thread)
        thread.start()

        self.handle_threads(threads)

    def handle_threads(self, threads, offset=0, i=0, dir=1):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue
            #offset = self.replace(thread, offset)
            sublime.status_message("SublimePeek: Help files for '%s' are ready to use." % (self.lang))
        threads = next_threads

        if len(threads):
            # This animates a little activity indicator in the status area
            before = i % 8
            after = (7) - before
            if not after:
                dir = -1
            if not before:
                dir = 1
            i += dir
            self.view.set_status('peek', 'SublimePeek [%s=%s]' % \
                (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(threads, offset, i, dir), 100)
            return

        self.view.erase_status('peek')


class GetHelpFiles(threading.Thread):
    def __init__(self, lang, path, timeout):
        # self.sel = sel
        # self.original = string
        self.lang = lang
        self.path = path
        self.timeout = timeout
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        try:
            # data files
            i = ['CSS', 'HTML', 'Python', 'JavaScript', 'PHP'].index(self.lang)
            d = ['css-mdn.json', 'html-mdn.json', 'python.json', 'js-mdn.json', 'php-ext.json'][i]
            url = 'https://raw.github.com/rgarcia/dochub/master/static/data/'

            # get data from json file at www.github.com/rgarcia/dochub
            data = json.load(urllib2.urlopen(url + d, timeout=self.timeout))

            # html elements
            note = [
                '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/CSS/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>',
                '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/HTML/Element/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>',
                '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a>.</p>',
                '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN.</p>',
                '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN.</p>'][i]

            html_page = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="chrome=1"><title>SublimePeek | Help for %s</title><link href="css/bootstrap.min.css" rel="stylesheet"><style type="text/css">  body {  padding-top: 10px;  padding-bottom: 20px;  padding-left: 10%;  padding-right: 10%;  }  .sidebar-nav {  padding: 9px 0;  }</style><link href="css/bootstrap-responsive.min.css" rel="stylesheet"><link href="css/custom.css" rel="stylesheet">  </head><body><div style="display: block; "><div id="4eea835f8cd2963cba000002" class="page-header"><h2>%s</h2><!--CONTENT-->%s<!--NOTE-->%s</div></div></body></html>'
            html_page = html_page.replace("10%", "10%%")

            # create folder if is doesn't exists
            if not os.path.exists(self.path):
                os.makedirs(self.path)

            # copy style files
            os.makedirs(self.path + 'css')
            distutils.dir_util.copy_tree(sublime.packages_path() + "/SublimePeek/css/DocHub", self.path + 'css')

            # get list of keywords
            ids = [item['title'] for item in data]

            # create mapping file for Python
            if self.lang == "Python":
                mapping_element = '\n{"from": "%s","to": "%s"}'
                f_map = open(self.path + "Python-mapping.json", "w")
                f_map.write("[")

            # define elements of mapping file as list
            if self.lang == "JavaScript":
                map_from = []
                map_to = []

            for id in ids:
                # get index
                i = ids.index(id)

                # get html
                if self.lang == "Python":
                    html = data[i]['html']
                    names = [item['name'] for item in data[i]['searchableItems']]
                    # domIds = [item['domId'] for item in data[i]['searchableItems']]
                    for k, name in enumerate(names):
                        f_map.write(mapping_element % (name, id))
                        if ids != ids[len(ids) - 1]:
                            f_map.write(',')
                else:
                    html = "".join(data[i]['sectionHTMLs'])
                html = html.replace("\n", "")

                # mapping file for javascript
                if self.lang == "JavaScript":
                    # split at . to get method name such as Array.length
                    fn = id.split(".")[-1]
                    # append to list for to, if function already exists
                    if fn in map_from:
                        k = map_from.index(fn)
                        map_to[k].append(id)
                    else:
                        map_from.append(fn)
                        map_to.append([id])

                # create note content
                if "%s" in note:
                    note_content = note % (id, id)
                else:
                    note_content = note

                # write html file
                f = open(self.path + id + ".html", "w")
                f.write((html_page % (id, id, html, note_content)).encode('utf-8'))
                f.close()

            if self.lang == "Python":
                f_map.write("\n]")
                f_map.close()

            # write javascript mapping file from list elements
            if self.lang == "JavaScript":
                # add if manually
                map_from.append("if")
                map_to.append(["if...else"])
                # structure of mapping.json file
                mapping_element = '\n  {\n      "from": "%s",\n      "to": %s\n  }'
                # open file for writing
                f_map = open(self.path + "JavaScript-mapping.json", "w")
                f_map.write("[")
                f_begin = True
                # iterate through elements in list
                for fn in map_from:
                    k = map_from.index(fn)
                    if len(map_to[k]) > 1 or map_to[k][0] != fn:
                        # get all to element as single string in list form
                        ids = "["
                        for j, id in enumerate(map_to[k]):
                            ids += '"' + id + '",'

                        ids = (ids + "]").replace(",]", "]")
                        # write element to mapping file
                        if not f_begin:
                            f_map.write(',')

                        f_begin = False
                        f_map.write(mapping_element % (fn, ids))

                # close mapping file
                f_map.write("\n]")
                f_map.close()

            # done!
            self.result = True
            return

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.reason))

        sublime.error_message(err)
        self.result = False

## Sublime Text 2 Plugin
#  Show quicklook window of selected R function

import sublime
import sublime_plugin
import subprocess
import re
import os
import json
import urllib2
import distutils.dir_util
from htmlentitydefs import name2codepoint

## mac os - quicklook
# /usr/bin/qlmanage -p [FILEPATH]

## linux - gloobus-preview
# /usr/bin/gloobus-preview [FILEPATH]

## load settings
settings = sublime.load_settings(u'SublimePeek.sublime-settings')


class SublimePeekCommand(sublime_plugin.TextCommand):
    lang = ""
    accessor = ""
    path = ""
    filepath = ""

    def run(self, edit):

        # get language
        self.lang = self.get_language()

        # check whether language is supported
        if not self.lang in settings.get("languages"):
            return
        # get accessor from settings
        self.accessor = settings.get(self.lang).get("accessor")

        # path for help files
        self.path = sublime.packages_path() + "/SublimePeek-%s-help/" % (self.lang)
        # check whether help files exists unless generated on the fly ("accessor" == "python")
        if not self.accessor == "python":
            if not os.path.exists(self.path):
                # compile help files or exit if compiling fails
                if not self.get_help_files(self.lang, self.path):
                    return

        # get keyword from selection
        keyword = self.get_keyword()
        sublime.status_message("SublimePeek: Help for '" + keyword + "'")

        # exit if no keyword defined
        if(keyword == ""):
            return

        # use mapping to get correct keyword
        if self.accessor == "mapping":
            # load mapping file
            map = json.load(open(self.path + '/%s-mapping.json' % (self.lang), "r"))
            map_from = [item['from'] for item in map]
            # exit if no help defined
            if not keyword in map_from:
                sublime.status_message("SublimePeek: No help file found for '" + keyword + "'.")
                return

            # use map to get keyword
            i = map_from.index(keyword)
            to = map[i]['to']
            if isinstance(to, str):
                keyword = to
            if isinstance(to, list):
                if len(to) > 1:
                    self.select_help_file(to, map[i]['sum'])
                else:
                    keyword = to[0]

        # generate help file using python (language specific)
        if self.accessor == "python":
            # generate python help file
            if self.lang == "Python":
                # set path for help file
                self.path = sublime.packages_path() + "/SublimePeek/"
                # set working dir
                os.chdir(self.path)
                # call pydoc to generate help file in html
                args = ['pydoc', '-w', keyword]
                p = subprocess.Popen(args)
                p.wait()
            # generate help files for other languages (e.g. )

        # show help file
        p = self.show_help(keyword)

        # remove help file if generated on the fly (self.accessor == "python")
        if self.accessor == "python":
            if p != -1:
                p.wait()
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)

    # call quick look to show help file
    def show_help(self, keyword):
        # set filepath of help file
        self.filepath = self.path + "%s.html" % (keyword)

        # quick look
        if os.path.isfile(self.filepath):
            args = ['/usr/bin/qlmanage', '-p', self.filepath]
            # qlmanage documentation
            # http://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man1/qlmanage.1.html
            p = subprocess.Popen(args)
            return p
        else:
            sublime.status_message("SublimePeek: No help file found for '" + keyword + "'.")

        return -1

    def get_language(self):
        lang_file = self.view.settings().get('syntax')
        lang = lang_file.split('/')
        lang = lang[len(lang) - 1].split('.')[0]
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

    # use ST2 show_quick_panel to let the user select a help files of multiple functions with the same name exsists (e.g. methods for different classes such as String.length and Array.length)
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

    # function to download and compule help files from DocHub
    # sorry, the function is a little messy
    def get_help_files(self, lang, path):
        # let's get started with a small message
        sublime.status_message("SublimePeek: Downloading and compiling help files for '" + lang + "'...")

        # prompt user
        if not sublime.ok_cancel_dialog("SublimePeek\nDo you want to download and compile the help files for '%s'?\n\n(Don't panic, ST2 freezes for a moment)" % (lang)):
            sublime.status_message("SublimePeek: Help files for '%s' are not installed." % (lang))
            return False

        # data files
        i = ['CSS', 'HTML', 'Python', 'JavaScript'].index(lang)
        d = ['css-mdn.json', 'html-mdn.json', 'python.json', 'js-mdn.json'][i]
        url = 'https://raw.github.com/rgarcia/dochub/master/static/data/'

        # html elements
        note = ['<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/CSS/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/HTML/Element/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a>.</p>', '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN.</p>'][i]

        html_page = '<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="chrome=1"><title>SublimePeek | Help for %s</title><link href="css/bootstrap.min.css" rel="stylesheet"><style type="text/css">  body {  padding-top: 10px;  padding-bottom: 20px;  padding-left: 10%;  padding-right: 10%;  }  .sidebar-nav {  padding: 9px 0;  }</style><link href="css/bootstrap-responsive.min.css" rel="stylesheet"><link href="css/custom.css" rel="stylesheet">  </head><body><div style="display: block; "><div id="4eea835f8cd2963cba000002" class="page-header"><h2>%s</h2><!--CONTENT-->%s<!--NOTE-->%s</div></div></body></html>'
        html_page = html_page.replace("10%", "10%%")

        # create folder if is doesn't exists
        if not os.path.exists(path):
            os.makedirs(path)

        # copy style files
        os.makedirs(path + 'css')
        distutils.dir_util.copy_tree(sublime.packages_path() + "/SublimePeek/help-compiler/DocHub-css", path + 'css')

        # get data from json file at www.github.com/rgarcia/dochub
        data = json.load(urllib2.urlopen(url + d))
        # get list of keywords
        ids = [item['title'] for item in data]

        # create mapping file for Python
        if lang == "Python":
            mapping_element = '\n{"from": "%s","to": "%s"}'
            f_map = open(path + "Python-mapping.json", "w")
            f_map.write("[")

        # define elements of mapping file as list
        if lang == "JavaScript":
            map_from = []
            map_to = []
            map_sum = []

        for id in ids:
            # get index
            i = ids.index(id)

            # get html
            if lang == "Python":
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
            if lang == "JavaScript":
                # split at . to get method name such as Array.length
                fn = id.split(".")[-1]
                # get the summary of the function
                summary = html.split("<p>")[1].split("</p>")[0]
                p = re.compile(r'<.*?>')
                summary = p.sub('', summary)[1:54] + "..."
                # add function to lists of mapping file
                # append to list for to, if function already exists
                if fn in map_from:
                    k = map_from.index(fn)
                    map_to[k].append(id)
                    map_sum[k].append(summary)
                else:
                    map_from.append(fn)
                    map_to.append([id])
                    map_sum.append([summary])

            # create note content
            if "%s" in note:
                note_content = note % (id, id)
            else:
                note_content = note

            # write html file
            f = open(path + id + ".html", "w")
            f.write((html_page % (id, id, html, note_content)).encode('utf-8'))
            f.close()

        if lang == "Python":
            f_map.write("\n]")
            f_map.close()

        # write javascript mapping file from list elements
        if lang == "JavaScript":
            # structure of mapping.json file
            mapping_element = '\n  {\n      "from": "%s",\n      "to": %s,\n      "sum": %s\n  }'
            # open file for writing
            f_map = open(path + "JavaScript-mapping.json", "w")
            f_map.write("[")
            # iterate through elements in list
            for fn in map_from:
                k = map_from.index(fn)
                # get all to and summary elements as single string in list form
                ids = "["
                summary = "["
                for j, id in enumerate(map_to[k]):
                    ids += '"' + id + '",'
                    summary += '"' + map_sum[k][j] + '",'

                ids = (ids + "]").replace(",]", "]")
                summary = (summary + "]").replace(",]", "]")
                # write element to mapping file
                f_map.write(mapping_element % (fn, ids, summary))
                if fn != map_from[- 1]:
                    f_map.write(',')

            # close mapping file
            f_map.write("\n]")
            f_map.close()

        # done!
        sublime.status_message("SublimePeek: Help files for '%s' are ready to use." % (lang))
        return True

    @staticmethod
    def unescape(s):
        "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
        return re.sub('&(%s);' % '|'.join(name2codepoint),
                  lambda m: unichr(name2codepoint[m.group(1)]), s)

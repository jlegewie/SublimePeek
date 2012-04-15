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

## mac os - quicklook
# /usr/bin/qlmanage -p [FILEPATH]

## linux - gloobus-preview
# /usr/bin/gloobus-preview [FILEPATH]

## load settings
settings = sublime.load_settings(u'SublimePeek.sublime-settings')


class SublimePeekCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        # get language
        lang = self.get_language()

        # check whether language is supported
        if not lang in settings.get("languages"):
            return

        # path for help files (check if accessor is not 'python')
        path = sublime.packages_path() + "/SublimePeek-%s-help/" % (lang)
        if not settings.get(lang).get("accessor") == "python" and not os.path.exists(path):
            if not self.get_help_files(lang, path):
                return

        # get keyword
        keyword = self.get_keyword()
        sublime.status_message("SublimePeek: Help for '" + keyword + "'")

        # exit if no keyword defined
        if(keyword == ""):
            return

        # use mapping to get correct help file
        if settings.get(lang).get("accessor") == "mapping":
            refs = json.load(open(path + '/stata-mapping.json', "r"))
            refs_from = [item['from'] for item in refs]
            i = refs_from.index(keyword)
            keyword = refs[i]['to']

        # Python help support
        if lang == "Python":
            # set path for help file
            path = sublime.packages_path() + "/SublimePeek/"
            # set working dir
            os.chdir(path)
            # call pydoc to generate help file in html
            args = ['pydoc', '-w', keyword]
            p = subprocess.Popen(args)
            p.wait()

        # set name of help file
        filepath = path + "%s.html" % (keyword)

        # quick look
        if os.path.isfile(filepath):
            args = ['/usr/bin/qlmanage', '-p', filepath]
            # qlmanage documentation
            # http://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man1/qlmanage.1.html
            p = subprocess.Popen(args)
        else:
            sublime.status_message("SublimePeek: No help file found for '" + keyword + "'.")

        # post-processing (language specific)
        if lang == "Python":
            p.wait()
            if os.path.isfile(filepath):
                os.remove(filepath)

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

    def get_help_files(self, lang, path):
        # prompt user
        if not sublime.ok_cancel_dialog("SublimePeek\nThe help files for '%s' do not exist. Do you want to download and compile the files now?" % (lang)):
            sublime.status_message("SublimePeek: Help files for '%s' do are not installed" % (lang))
            return False

        # let's get started with a small message
        sublime.status_message("SublimePeek: Downloading and compiling help files for '" + lang + "'...")

        # data files
        i = ['CSS', 'HTML', 'Python'].index(lang)
        d = ['css-mdn.json', 'html-mdn.json', 'python.json'][i]
        url = 'https://raw.github.com/rgarcia/dochub/master/static/data/'

        # html elements
        note = ['<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/CSS/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a> from MDN at <a target="_blank" href="https://developer.mozilla.org/en/HTML/Element/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '<p class="source-link">This content was sourced by <a href="http://dochub.io/">DocHub</a>.</p>'][i]

        html_page = '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="chrome=1"><title>SublimePeek | Help for %s</title><link href="css/bootstrap.min.css" rel="stylesheet"><style type="text/css">  body {  padding-top: 10px;  padding-bottom: 20px;  padding-left: 10%;  padding-right: 10%;  }  .sidebar-nav {  padding: 9px 0;  }</style><link href="css/bootstrap-responsive.min.css" rel="stylesheet"><link href="css/custom.css" rel="stylesheet">  </head><body><div style="display: block; "><div id="4eea835f8cd2963cba000002" class="page-header"><h2>%s</h2><!--CONTENT-->%s<!--NOTE-->%s</div></div></body>'
        html_page = html_page.replace("10%", "10%%")

        mapping_element = '\n{"from": "%s","to": "%s"}'

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
            f_map = open(path + "Python-mapping.json", "w")
            f_map.write("[")

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

            # create note content note
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

        sublime.status_message("SublimePeek: Help files for '%s' are ready to use." % (lang))

        return True

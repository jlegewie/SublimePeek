## Sublime Text 2 Plugin
#  Show quicklook window of selected R function

import sublime
import sublime_plugin
import subprocess
import re
import os.path

## mac os - quicklook
# /usr/bin/qlmanage -p '/Users/jpl2136/Desktop/anette/Causal Inference NYU/Assigments/4 Matching Scores/psbal.ado'

## linux - gloobus-preview
# /usr/bin/gloobus-preview filelocation


class SublimePeekCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        # get language
        lang = self.get_language()

        # check path for help files
        path = sublime.packages_path() + "/SublimePeek-%s-help/" % (lang)
        if not os.path.exists(path):
            return

        # get keyword
        keyword = self.get_keyword()
        sublime.status_message("SublimePeek: Help for '" + keyword + "'")

        # exit if no keyword defined
        if(keyword == ""):
            return

        # set name of help file
        filepath = path + "%s.html" % (keyword)

        # quick look
        if os.path.isfile(filepath):
            args = ['/usr/bin/qlmanage', '-p', filepath]
            # qlmanage documentation
            # http://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man1/qlmanage.1.html
            subprocess.Popen(args)
        else:
            sublime.status_message("SublimePeek: No help file found for '" + keyword + "'.")

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
            # if cursor after (, return help for function before (
            if self.view.substr(pos - 1) == "(":
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

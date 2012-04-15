#!/usr/bin/python

## DocHub-help.py creates the help files for HTML, CSS, and Python
# 1) download and unpack DocHub (https://github.com/rgarcia/dochub)
# 2) set the location variables
# 3) run this file

# set locations
# loc_DucHub_data = '/Users/jpl2136/Documents/coding/rgarcia-dochub-07a2d15/static/data/'
loc_st2_packages = '/Users/jpl2136/Library/Application Support/Sublime Text 2/Packages/'

# import libraries
import json
import os
import distutils.dir_util
import urllib2

# data files
lang = ['CSS', 'HTML', 'Python']
data_files = ['css-mdn.json', 'html-mdn.json', 'python.json']
url = 'https://raw.github.com/rgarcia/dochub/master/static/data/'

# html elements
note = ['<p class="source-link">Content sourced from MDN at <a target="_blank" href="https://developer.mozilla.org/en/CSS/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '<p class="source-link">Content sourced from MDN at <a target="_blank" href="https://developer.mozilla.org/en/HTML/Element/%s">https://developer.mozilla.org/en/CSS/%s</a>.</p>', '']

container = '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="chrome=1"><title>SublimePeek | Help for %s (based on DocHub)</title><link href="css/bootstrap.min.css" rel="stylesheet"><style type="text/css">  body {  padding-top: 10px;  padding-bottom: 20px;  padding-left: 10%;  padding-right: 10%;  }  .sidebar-nav {  padding: 9px 0;  }</style><link href="css/bootstrap-responsive.min.css" rel="stylesheet"><link href="css/custom.css" rel="stylesheet">  </head><body><div style="display: block; "><div id="4eea835f8cd2963cba000002" class="page-header"><h2>%s</h2><!--CONTENT-->%s<!--NOTE-->%s</div></div></body>'.replace("10%", "10%%")

container_json = '\n{"from": "%s","to": "%s"}'

# iterate through data files
for j, l in enumerate(lang):
    print l

    # output location
    loc = loc_st2_packages + 'SublimePeek-' + lang[j] + '-help/'
    # create folder if is doesn't exists
    if not os.path.exists(loc):
        os.makedirs(loc)

    # copy style files
    distutils.dir_util.copy_tree(loc_st2_packages + "SublimePeek/help-compiler/DocHub-css", loc + 'css')

    # get data from json file at www.github.com/rgarcia/dochub
    data = json.load(urllib2.urlopen(url + data_files[j]))
    # get list of keywords
    ids = [item['title'] for item in data]

    # create mapping file for Python
    if l == "Python":
        f_map = open(loc + "Python-mapping.json", "w")
        f_map.write("[")

    for id in ids:
        # get index
        i = ids.index(id)
        # get html
        if l == "Python":
            html = data[i]['html']
            names = [item['name'] for item in data[i]['searchableItems']]
            domIds = [item['domId'] for item in data[i]['searchableItems']]
            for k, name in enumerate(names):
                f_map.write(container_json % (name, id))
                if ids != ids[len(ids) - 1]:
                    f_map.write(',')
        else:
            html = "".join(data[i]['sectionHTMLs'])
        html = html.replace("\n", "")
        # create note content note
        if note[j] != "":
            note_content = note[j] % (id, id)
        else:
            note_content = ""
        # write html file
        f = open(loc + id + ".html", "w")
        f.write((container % (id, id, html, note_content)).encode('utf-8'))
        f.close()

    if l == "Python":
        f_map.write("\n]")
        f_map.close()

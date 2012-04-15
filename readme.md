# SublimePeek
SublimePeek provides quick access to documentation by opening help files in Quick Look. Currently, the plugin only runs on Mac OS but it can be extended to work on other unix systems using gloobus-preview as well as Windows using maComfort. The only supported language right now are HTML, CSS, Python and R but again, the plugin can be extended to support other languages. 

# Installation
To install SublimePeek, clone or copy this repos to your ST2 packages folder. After finalizing the first version, I will add the plugin to package control.

#### Python
The python help files are generated on the fly using `pydoc` so that python should work right away.

#### HTML and CSS
The help files for HTML and CSS are based on [DocHub](http://dochub.io/) and first need to be downloaded and compiled. SublimePeek can do all the work so that you only need to open a css or html file and start using SublimePeek. The first time you will be asked whether you want to install the files during which ST2 is unresponsive. Afterwards, SublimePeek should just work.

#### R
For R, you have to install the help files yourself. They can be installed from a separate repos    https://github.com/jlegewie/SublimePeek-R-help, which should be cloned/copied to the `[ST2 Packages]/SublimePeek-R-help` folder. Alternatively, SublimePeek contains a help compiler, which allows you to create the help files yourself. Just look in the SublimePeek packages folder under help-compiler for the file `R-help.r`. The advantage of compiling the R help files yourself is that the SublimePeek-R-help repos only contains the help files for the base packages. Using the R help compiler creates the help files for all installed R packages. 

# Support for Unix and Windows
Currently, the plugin only runs on Mac OS but it can be extended to work on other unix systems using gloobus-preview as well as Windows using maComfort. I personally don't have a unix or windows system but it should be pretty easy to add support. Drop me a line and we can make it work.

# Support for other Languages
Adding support for other languages is easy. You either need help files that are called like the respective function (i.e. one help file for each function) or help files that are linked to the function name with a simple json database. For R, I generated these help files with a short script that iterates through all objects in all installed packages and extracts the help file for each function (see the R-help.r file in the help-compiler folder). These files should be in a format that is supported by Quick Look (Mac), gloobus-preview (Linux), and maComfort (Windows) such as html or simple text files. I am happy to provide more information as soon as someone wants to add support for other languages. 
 
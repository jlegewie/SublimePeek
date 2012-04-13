# SublimePeek
SublimePeek provides quick access to documentation by opening help files in Quick Look. Currently, the plugin only runs on Mac OS but it can be extended to work on other unix systems using gloobus-preview as well as Windows using maComfort. The only supported language right now are Python and R but again, the plugin can be extended to support other languages. 

# Installation
To install SublimePeek, clone or copy this repos to your ST2 packages folder. After finalizing the first version, I will add the plugin to package control.
For Python, SublimePeek should work right away. For other languages (currently only R), you also have to get the actual help files. The help files are relative large and contain thousands of file.They can be installed from separate repos for each language such as SublimePeek-R-help at https://github.com/jlegewie/SublimePeek-R-help. Alternatively, SublimePeek contains help compilers, which allow you to create the help files yourself. Just look in the SublimePeek packages folder under help-compiler and you will find some code that allows you to compile the help files yourself. For R, the advantage also is that the SublimePeek-R-help only contains the help files for the base packages. Using the R help compiler creates the help files for all installed R packages. 

# Support for Unix and Windows
Currently, the plugin only runs on Mac OS but it can be extended to work on other unix systems using gloobus-preview as well as Windows using maComfort. I personally don't have a unix or windows system but it should be pretty easy to add support. Drop me a line and we can make it work.

# Support for other Languages
Adding support for other languages is easy. You either need help files that are called like the respective function (i.e. one help file for each function) or help files that are linked to the function name with a simple json database. For R, for example, I generated these help files with a short script that iterates through all objects in all installed packages and extracts the help file for each function (see the R-help.r file in the help-compiler folder). These files should be in a format that is supported by Quick Look (Mac), gloobus-preview (Linux), and maComfort (Windows) such as html or simple text files. I am happy to provide more information as soon as someone wants to add support for other languages. 
 
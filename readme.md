# SublimePeek
SublimePeek provides quick access to documentation by opening help files in Quick Look. The plugin supports _HTML_, _CSS_, _JavaScript_, _PHP_, _Python_, _Ruby_, _R_, and _Stata_. Support for other languages can be added easily.

**Supported Languages:** HTML, CSS, JavaScript, PHP, Python, Ruby, R, and Stata

## Installation
(instructions based on https://github.com/Kronuz/SublimeLinter and ZoteroQuickLook)


**With the Package Control plugin:** The easiest way to install SublimePeek is through Package Control. Instructions to install Package Control can be found here: http://wbond.net/sublime_packages/package_control/installation

Once you install Package Control, restart ST2 and bring up the Command Palette (``Command+Shift+P`` on OS X, ``Control+Shift+P`` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select SublimePeek when the list appears. The advantage of using this method is that Package Control will automatically keep SublimePeek up to date with the latest version.

**Without Git:** Download the latest source from [GitHub](http://github.com/jlegewie/SublimePeek) and copy the SublimePeek folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory: `git clone git://github.com/jlegewie/SublimePeek.git`


The "Packages" directory is located at:

* OS X: `~/Library/Application Support/Sublime Text 2/Packages/`
* Linux: `~/.config/sublime-text-2/Packages/`
* Windows: `%APPDATA%/Sublime Text 2/Packages/`

## Required Software on Linux and Windows
On OS X the plugin uses native Quick Look feature through qlmanage command so that no additional software or configuration is required. On Linux and Windows, you need to install additional software.

### Linux
Note: Linux support is preliminary and untested. Please let me know if it works or if it doesn't!!

On Linux the user must install Gloobus, which is a preview software. On Ubuntu you can do this by running the following commands in terminal:  

    sudo add-apt-repository ppa:gloobus-dev/gloobus-preview 
    sudo apt-get update 
    sudo apt-get upgrade 
    sudo apt-get install gloobus-preview

For other distributions and versions the installation might be different.

### Windows
On Windows you must install [maComfort](http://rafaelklaus.com/macomfort/) version 1.5 or later. If maComfort is not installed in `C:\Program Files\maComfort\` or `C:\Program Files (x86)\maComfort\`, you have to set the option `custom_executable` to the correct location. The option should take this form (just replace the first element in the list): `["C:\\Program Files\\maComfort\\maComfort.exe", "-ql"]`

## Support for Different Languages

### Python and Ruby
The python help files are generated on the fly using `pydoc` for Python and `ri` for Ruby so that both languages should work right away.

### HTML, CSS, JavaScript, and PHP
The help files for HTML, CSS, JavaScript, and PHP are based on [DocHub](http://dochub.io/). They first need to be downloaded and compiled. SublimePeek can do all the work for you. So just open a corresponding file and start using SublimePeek. The first time you will be asked whether you want to download and compile the files, which takes a moment.

### R and Stata
For R, you have to install the help files yourself. They are available as an additional package from Package Control (`SublimePeek-R-help`) or on a separate GitHub repos at https://github.com/jlegewie/SublimePeek-R-help.
Alternatively, SublimePeek contains a help compiler, which allows you to create the help files yourself. Just look in the SublimePeek packages folder under `help-compiler` for the file `R-help.r`. The advantage of compiling the R help files yourself is that the SublimePeek-R-help repos only contains the help files for the base packages and ggplot2. Using the R help compiler creates the help files for all installed R packages.

The Stata help files are currently not available as a separate package but can easily be compiled using the Stata do-file `Stata-help.r` in the `help-compiler` folder. If people are interested in these files, I can add them as an additional ST2 package.

## Using SublimePeek
Just select a function, and press `super+shift+h`. If the language is supported by SublimePeek, you should now see a Quick Look window with the documentation for the function. Actually, you don't have to select the function. SublimePeek automatically uses the word at the current cursor position or the word before the opening `(`. `json.lo|ad`, however, does not work because the dot interrupts the word. If no help file is found, SublimePeek displays an overview of all available help files from which the user can quickly pick. 

### Overview of Help Files
For all languages except Python and Ruby, SublimePeek can show an overview of all available help topics based on the familiar ST2 quick select panel (the same as the command panel, or the one for jumping from project to project). SublimePeek shows the overview, if no matching help file is found for the current selection. To bring up the overview directly, just make sure that your current selection is not meaningful and you can quickly browse all help topics.

## Support for other Languages
Adding support for other languages is easy. You either need help files that are called like the respective function (i.e. one help file for each function) or help files that are linked to the function name with a simple json database. For R, I generated these help files with a short script that iterates through all objects in all installed packages and extracts the help file for each function (see the R-help.r file in the help-compiler folder). These files should be in a format that is supported by Quick Look (Mac), gloobus-preview (Linux), and maComfort (Windows) such as html or simple text files. I am happy to provide more information when someone wants to add support for other languages. 
 
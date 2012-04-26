## script to get R help files
# This script generates R help files for all installed packages for SublimePeek 
# and moves the style file R.css to the correct location.
# Help files for the base packages and ggplot2 are also available at 
# https://github.com/jlegewie/SublimePeek-R-help

## USER PARAMETERS ##
# set the loc variable to the ST2 Packages Folder (don't forget the / at the end)
loc      = '~/Library/Application Support/Sublime Text 2/Packages/'
# the default setting uses all installed packages. Alternative: vector of packages
pkg.user = rownames(installed.packages())

# function to get html formated help
# adopted from stackoverflow
getHTMLhelp = function(...) { 
    h = help(...)
    if (length(h)>0) {
        out=capture.output(
                tools:::Rd2HTML(utils:::.getHelpFile(h[1]))
            )
    } else {
        out=""
    }
    # return(htmlspecialchars(out))
    return(paste(out,"\n",sep=""))
}

# deal with special HTML/XML characters
htmlspecialchars <- function(string) {
    # x = c("&", '"', "<", ">")
    # subx = c("&amp;", "&quot;", "&lt;", "&gt;")
    x = c("&")
    subx = c("&amp;")
    for (i in seq_along(x)) {
        string = gsub(x[i], subx[i], string, fixed = TRUE)
    }
    string
}

# create folder for R help files
dir.create(paste(loc,"SublimePeek-R-help/",sep=""),showWarnings=FALSE)

# get main packages
pkg.main = names(na.omit(installed.packages()[, 'Priority']))

# all packages
pkg.all = unique(c(pkg.main,pkg.user))
pkg.all = pkg.all[!(pkg.all %in% c("survival","tcltk","cem","debug"))]
# these packages crashed my R so I excluded them...

# load packages
sapply(pkg.all, library, character.only = TRUE)

# loaded packages
pkg.loaded=(.packages()) 
k = length(pkg.loaded)

# iterate through packages
n.f = 0
n.p = 0
for(pkg in pkg.loaded) {
    n.p = n.p+1
    cat("creating help files for '", pkg,"' (",n.p,"/",k,")...",sep="")
    # name of package environment
    env =paste("package",pkg,sep=":")
    # get functions in packages environment
    fn.pkg  =ls(env, all.names = FALSE)
    # remove functions
    idx = grep("[<>&@:\\?\\{\\(\\)\\[\\^\\*\\$!%/\\|\\+=~\\-]", fn.pkg)
    if (length(idx)) fn.pkg = fn.pkg[-idx]
    idx <- grep("^(\\._|\\.\\.)", fn.pkg)
    if (length(idx)) fn.pkg = fn.pkg[-idx]

    # iterate through functions in package
    for(fn in fn.pkg) {
        obj = get(fn, envir = as.environment(env))
        if (mode(obj) == "function") {
            n.f = n.f+1
            cat(getHTMLhelp(fn),file= paste(loc,"SublimePeek-R-help/",fn,".html",sep=""))   
        }
    }
    cat(" done!\n")
}

# copy style file (R.css) to folder with R help files
file.copy(paste(loc,"SublimePeek/css/R.css",sep=""),paste(loc,"SublimePeek-R-help/R.css",sep=""))

# end of file ggplot
cat("\n\nHelp files from ",n.f," functions in ", n.p," packages saved to JSON.\n")






* set st2 packages location
global st2 "~/Library/Application Support/Sublime Text 2/Packages"

* install required stata packages
ssc install hlp2html, replace 
ssc install log2html, replace
net install getcmds, from("http://www.stata.com/users/jpitblado")

* create stata help folder
cap mkdir "$st2/SublimePeek-Stata-help"

* change working directory to correct location
cd "$st2/SublimePeek-Stata-help"

* copy style file
copy "$st2/SublimePeek/css/Stata.css" "$st2/SublimePeek-Stata-help/Stata.css", replace

* get 'all' stata commands 
global path_cmd "$st2/SublimePeek-Stata-help/stata-cmd.txt"
getcmds using "$path_cmd", replace 

* open reference json file
file open file_json using "$st2/SublimePeek-Stata-help/stata-mapping.json", write replace
file write file_json  "[" _n

* open command file
file open file_cmd using "$path_cmd", read

* loop through commands in cmd list
file read file_cmd cmd
local first 1
while r(eof)==0 {
	display "`cmd': " _c
	* get full stata command and help alias if defined
	unabcmd `cmd'
	local cmd_full = r(cmd)
	cap _findhlpalias `cmd_full'
	if (_rc==0) local cmd_full = r(name)
	dis "`cmd_full'"
	* create help file if it doesn't exists
	cap confirm file "$st2/SublimePeek-Stata-help/`cmd_full'.html"
	if (_rc!=0) {
		cap hlp2html, fnames("`cmd_full'") linesize(120) css("Stata.css") replace
		cap erase "`cmd_full'.smcl"
	}

	* create reference json file
	if ("`cmd'"!="`cmd_full'") {
		if(`first'!=1) file write file_json "," _n
		file write file_json _tab "{" _n
		file write file_json _tab _tab `""from": "`cmd'","' _n
		file write file_json _tab _tab `""to": "`cmd_full'""' _n
		file write file_json _tab "}" 
		local first 0
	}

	* read new line in file
	file read file_cmd cmd
}
* close files
file close file_cmd
file write file_json  _n "]"
file close file_json

* remove command list file
erase "$st2/SublimePeek-Stata-help/stata-cmd.txt"

* PROBLEM:
* replace->generate
* global,local->macro

* think about adding the list of commands from language definition


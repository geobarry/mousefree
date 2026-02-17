os: windows
os: windows
and mode: user.zen
-
# NOTE: In old Microsoft Word .doc documents, text is garbled when there are bullets present
# Please update to .docx; there is no way to fix this from our end

# ABOUT NAVIGATION TARGETS (i.e. <user.win_nav_target>)
# All navigation targets require directional specification,
#   e.g. "Select next 'hippopotamus'" NOT "Select 'hippopotamus'" 
#   Directional specifications are "previous", "next" and "inside".
# 'Dynamic' navigation targets are searched for when there are no explicit prefixes,
#   e.g. "Select next 'hippopotamus'".
#	Because talon only has to choose from a limited section of text,
#	recognition rates are usually very high.
#   Dynamic targets only work in applications that implement Microsoft's UIAutomation text pattern
# 'Constructed' navigation targets are searched for when there is an explicit prefix,
#   e.g. "Select next *word* 'hippopotamus'" 
#   Available prefixes include "word" "phrase" "character" "number" and formatters.
#   These require talon to match your spoken words exactly to the text in the 
#   document, so recognition rates will be lower. 
#   Constructed targets work in all applications.

# e.g. "GO BEFORE next 'hippopotamus'"
go {user.before_or_after} [<user.ordinals>] <user.win_nav_target>:
	user.winax_go_text(win_nav_target,before_or_after,ordinals or 1)

# e.g. "SELECT previous 'hippopotamus'"
[{user.text_search_unit}] select [<user.ordinals>] <user.win_nav_target>: user.winax_select(win_nav_target,ordinals or 1,text_search_unit or '')

# SELECT FROM...TO... e.g. "select from previous 'hippopotamus' to phrase 'charging at me'"
#	Note that second target must be explicitly prefixed, we cannot have two dynamic targets at once
[{user.text_search_unit}] select from [<user.ordinals>] <user.win_nav_target> to [<user.ordinals>] <user.explicit_target>:
	user.winax_select_from_to(win_nav_target,explicit_target,ordinals or 1, text_search_unit or '')

# e.g. "EXTEND after next 'hippopotamus'"
[{user.text_search_unit}] extend [(to|until)] {user.before_or_after} [<user.ordinals>] <user.win_nav_target>$:
	user.winax_extend_selection(win_nav_target,before_or_after,ordinals or 1,text_search_unit or '')

# e.g. "PHONES previous 'lynx'"
phones [<user.ordinals>] <user.win_nav_target>$: user.winax_phones_text(win_nav_target,ordinals or 1)

# e.g. "FORMAT title next 'gloria'"
format <user.formatters> [<user.ordinals>] <user.win_nav_target>$:
	user.winax_format_text(user.formatters, win_nav_target,ordinals or 1)

# e.g. "REPLACE previous 'hippopotamus' with word 'rhinoceros'"
#	Note that second target must be explicitly prefixed, we cannot have two dynamic targets at once
replace [<user.ordinals>] <user.win_nav_target> with <user.constructed_text>:
	user.winax_replace_text(constructed_text, win_nav_target,ordinals or 1)

# e.g. "DELETE next 'hippopotamus'"
delete [<user.ordinals>] <user.win_nav_target>$:
	user.winax_replace_text("", win_nav_target,ordinals or 1)

# e.g. "ADD/REMOVE quotes around previous 'hippopotamus'"
place {user.delimiter_pair} around [<user.ordinals>] <user.win_nav_target>$:
	user.winax_add_delimiters(delimiter_pair,win_nav_target,ordinals or 1)
remove {user.delimiter_pair} around [<user.ordinals>] <user.win_nav_target>$:
	user.winax_remove_delimiters(delimiter_pair,win_nav_target,ordinals or 1)

# e.g. "INSERT word 'hungry' before next 'hippopotamus'"
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] <user.win_nav_target>:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,win_nav_target)


# FOLLOWING SEARCH UNIT COMMANDS ONLY WORK IN APPLICATIONS THAT IMPLEMENT TEXT PATTERNS
# SELECT CURRENT PARAGRAPH OR OTHER UNIT
select {user.text_search_unit}$: user.winax_select_unit(text_search_unit)

# GO UP/DOWN BY SEARCH UNIT e.g. "go up one paragraph", "down seven pages"
[go] {user.search_dir} <number_small> {user.text_search_unit}$: 
	user.winax_move_by_unit(text_search_unit,search_dir,number_small)
	
# EXTEND/EXPAND SELECTION
extend right$: user.winax_expand_selection(false,true)
extend left$: user.winax_expand_selection(true,false)
expand [<number_small>] {user.text_search_unit}$: user.winax_expand_selection(true,true,text_search_unit or "character",number_small or 1)

# EXTEND BY SEARCH UNIT e.g. "extend down one paragraph"
extend {user.search_dir} [<number_small>] {user.text_search_unit}$:
	user.winax_extend_by_unit(text_search_unit,search_dir,number_small or 1)
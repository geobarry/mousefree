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
# 'Explicit' navigation targets are searched for when there is an explicit prefix,
#   e.g. "Select next *word* 'hippopotamus'" 
#   Available prefixes include "word" "phrase" "character" "number" and formatters.
#   These require talon to match your spoken words exactly to the text in the 
#   document, so recognition rates will be lower. 
#   Explicit targets work in all applications.

# GO BEFORE/AFTER e.g. "go before next 'hippopotamus'"
go {user.before_or_after} [<user.ordinals>] <user.win_nav_target>:
	user.winax_go_text(win_nav_target,before_or_after,ordinals or 1)

# SELECT e.g. "select next 'hippopotamus'"
[{user.text_search_unit}] select [<user.ordinals>] <user.win_nav_target>: user.winax_select(win_nav_target,ordinals or 1,text_search_unit or '')

# SELECT FROM...TO... e.g. "select from previous 'hippopotamus' to phrase 'charging at me'"
#	Note that second target must be explicitly prefixed, we cannot have two dynamic targets at once
select from <user.win_nav_target> to [<user.ordinals>] <user.explicit_target>:
	user.winax_select(win_nav_target,ordinals or 1,text_search_unit or '')
	user.winax_extend_selection(explicit_target,"DOWN","AFTER",ordinals or 1)

# EXTEND e.g. "extend after next 'hippopotamus'"
extend {user.before_or_after} [<user.ordinals>] <user.win_nav_target>$:
	user.winax_extend_selection(win_nav_target,before_or_after,ordinals or 1)

# FOLLOWING SEARCH UNIT COMMANDS ONLY WORK IN APPLICATIONS THAT IMPLEMENT TEXT PATTERNS
# EXTEND BY SEARCH UNIT e.g. "extend down one paragraph"
extend {user.search_dir} [<number_small>] {user.text_search_unit}$:
	user.winax_extend_by_unit(text_search_unit,search_dir,number_small or 1)

# GO UP/DOWN BY SEARCH UNIT e.g. "go up one paragraph", "down seven pages"
[go] {user.search_dir} <number_small> {user.text_search_unit}$: 
	user.winax_move_by_unit(text_search_unit,search_dir,number_small)
	
# SELECT A PARAGRAPH OR OTHER UNIT
select {user.text_search_unit}$: user.winax_select_unit(text_search_unit)


# HOMOPHONE CORRECTION
	# example spoken forms:
	#	phones previous ceiling
	#	phones third next word there
phones [<user.ordinals>] next {user.win_next_dyn_nav_trg}$: user.winax_phones_text(win_next_dyn_nav_trg,"DOWN",ordinals or 1)
phones [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$: user.winax_phones_text(win_previous_dyn_nav_trg,"UP",ordinals or 1)
phones [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$: user.winax_phones_text(win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
phones [<user.ordinals>] any {user.win_any_dyn_nav_trg}$: user.winax_phones_text(win_any_dyn_nav_trg,"BOTH",ordinals or 1)

phones [<user.ordinals>] {user.search_dir} <user.win_nav_target>$: user.winax_phones_text(win_nav_target,search_dir,ordinals or 1)


# FORMATTING CORRECTION
	# example spoken forms:
	#	format title previous brown
	#	format upper snake next phrase fox jumped over the lazy dog
format <user.formatters> [<user.ordinals>] next {user.win_next_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_next_dyn_nav_trg,"DOWN",ordinals or 1)
format <user.formatters> [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_previous_dyn_nav_trg,"UP",ordinals or 1)
format <user.formatters> [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
format <user.formatters> [<user.ordinals>] any {user.win_any_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_any_dyn_nav_trg,"BOTH",ordinals or 1)

format <user.formatters> [<user.ordinals>] {user.search_dir} <user.win_nav_target>: user.winax_format_text(user.formatters, win_nav_target,search_dir,ordinals or 1)

format <user.formatters> <user.formatters> [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_next_dyn_nav_trg,"DOWN",ordinals or 1)
	user.winax_format_text(formatters_2, win_next_dyn_nav_trg,"DOWN",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_previous_dyn_nav_trg,"UP",ordinals or 1)
	user.winax_format_text(formatters_2, win_previous_dyn_nav_trg,"UP",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_inside_dyn_nav_trg,"DOWN",ordinals or 1)
	user.winax_format_text(formatters_2, win_inside_dyn_nav_trg,"DOWN",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_any_dyn_nav_trg,"UP",ordinals or 1)
	user.winax_format_text(formatters_2, win_any_dyn_nav_trg,"UP",ordinals or 1)

format <user.formatters> <user.formatters> [<user.ordinals>] {user.search_dir} <user.win_nav_target>:
	user.winax_format_text(formatters_1, win_nav_target,search_dir,ordinals or 1)
	user.winax_format_text(formatters_2, win_nav_target,search_dir,ordinals or 1)



# TEXT REPLACEMENT
replace [<user.ordinals>] next {user.win_next_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_next_dyn_nav_trg,"DOWN",ordinals or 1)
replace [<user.ordinals>] previous {user.win_previous_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_previous_dyn_nav_trg,"UP",ordinals or 1)
replace [<user.ordinals>] inside {user.win_inside_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
replace [<user.ordinals>] any {user.win_any_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_any_dyn_nav_trg,"BOTH",ordinals or 1)

replace [<user.ordinals>] {user.search_dir} <user.win_nav_target> with <user.constructed_text>:
	user.winax_replace_text(constructed_text, win_nav_target,search_dir,ordinals or 1)

# DELIMITERS
add {user.delimiter_pair} around [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_add_delimiters(delimiter_pair,win_next_dyn_nav_trg,"DOWN",ordinals or 1)
add {user.delimiter_pair} around [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_add_delimiters(delimiter_pair,win_previous_dyn_nav_trg,"UP",ordinals or 1)	
add {user.delimiter_pair} around [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_add_delimiters(delimiter_pair,win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
add {user.delimiter_pair} around [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_add_delimiters(delimiter_pair,win_any_dyn_nav_trg,"BOTH",ordinals or 1)

remove {user.delimiter_pair} around [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_remove_delimiters(delimiter_pair,win_next_dyn_nav_trg,"DOWN",ordinals or 1)
remove {user.delimiter_pair} around [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_remove_delimiters(delimiter_pair,win_previous_dyn_nav_trg,"UP",ordinals or 1)	
remove {user.delimiter_pair} around [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_remove_delimiters(delimiter_pair,win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
remove {user.delimiter_pair} around [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_remove_delimiters(delimiter_pair,win_any_dyn_nav_trg,"BOTH",ordinals or 1)

# TEXT REMOVAL
delete [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_replace_text("", win_next_dyn_nav_trg,"DOWN",ordinals or 1)
delete [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_replace_text("", win_previous_dyn_nav_trg,"UP",ordinals or 1)
delete [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_replace_text("", win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
delete [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_replace_text("", win_any_dyn_nav_trg,"BOTH",ordinals or 1)

delete [<user.ordinals>] {user.search_dir} <user.win_nav_target>:
	user.winax_replace_text("", win_nav_target,search_dir,ordinals or 1)



extend right$: user.winax_expand_selection(false,true)
extend left$: user.winax_expand_selection(true,false)
expand [<number_small>] {user.text_search_unit}$: user.winax_expand_selection(true,true,text_search_unit or "character",number_small or 1)

# INSERTION
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,"DOWN",win_next_dyn_nav_trg)
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,"UP",win_previous_dyn_nav_trg)
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,"INSIDE",win_inside_dyn_nav_trg)
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,"BOTH",win_any_dyn_nav_trg)
	
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] {user.search_dir} <user.win_nav_target>:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,search_dir,win_nav_target)



# convenient deleting from current cursor position
delete until [<user.ordinals>] next {user.win_next_dyn_nav_trg}:
	user.winax_extend_selection(win_next_dyn_nav_trg,"DOWN","BEFORE",ordinals or 1)
	edit.delete()
delete until [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}:
	user.winax_extend_selection(win_previous_dyn_nav_trg,"UP","AFTER",ordinals or 1)
	edit.delete()
delete through [<user.ordinals>] next {user.win_next_dyn_nav_trg}:
	user.winax_extend_selection(win_next_dyn_nav_trg,"DOWN","AFTER",ordinals or 1)
	edit.delete()
delete through [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}:
	user.winax_extend_selection(win_previous_dyn_nav_trg,"UP","BEFORE",ordinals or 1)
	edit.delete()

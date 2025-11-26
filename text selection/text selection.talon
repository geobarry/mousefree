os: windows
os: windows
and mode: user.zen
-
# NOTE: In old Microsoft Word .doc documents, text is garbled when there are bullets present
# Please update to .docx; there is no way to fix this from our end

# ABOUT NAVIGATION TARGETS
# "Dynamic" navigation targets (win_next_dyn_nav_trg, win_previous_dyn_nav_trg) 
#	are determined on the fly from text before or after cursor. 
#	Because talon only has to choose from a limited section of text,
#	recognition rates are usually very high.
# "Static" navigation targets (win_nav_target) require talon matching your 
#	spoken words exactly to the text in the document, so recognition rates can 
#	be much lower. To distinguish these and favour dynamic navigation targets, 
#	static targets typically require prefix identifiers, e.g. "word" or "phrase"
#	Static targets also include alphanumeric characters, optionally prefixed with
#	"letter" or "character"

# NAVIGATION COMMANDS
	# example spoken forms:
	#   go before next hippopotamus
	#	go after second previous letter cap
	#	up four lines
	#	down two paragraphs
  	#	go up to hippopotamus

go {user.before_or_after} [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_go_text(win_next_dyn_nav_trg,"DOWN",before_or_after,ordinals or 1)
go {user.before_or_after} [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_go_text(win_previous_dyn_nav_trg,"UP",before_or_after,ordinals or 1)
go {user.before_or_after} [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_go_text(win_inside_dyn_nav_trg,"INSIDE",before_or_after,ordinals or 1)
go {user.before_or_after} [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_go_text(win_any_dyn_nav_trg,"BOTH",before_or_after,ordinals or 1)

go {user.before_or_after} [<user.ordinals>] {user.search_dir} <user.win_nav_target>$:
	user.winax_go_text(win_nav_target,search_dir,before_or_after,ordinals or 1)
{user.search_dir} <number_small> {user.text_search_unit}$: 
	user.winax_move_by_unit(text_search_unit,search_dir,number_small)


# SELECTION
	# example spoken forms:
	#   select next hippopotamus
	#	select previous letter cap
	#	select next bang
	#   select third previous brief exponent
	#	select paragraph
[{user.text_search_unit}] select [<user.ordinals>] next {user.win_next_dyn_nav_trg}$: user.winax_select_text(win_next_dyn_nav_trg,"DOWN",ordinals or 1,text_search_unit or '')
[{user.text_search_unit}] select [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$: user.winax_select_text(win_previous_dyn_nav_trg,"UP",ordinals or 1,text_search_unit or '')
[{user.text_search_unit}] select [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$: user.winax_select_text(win_inside_dyn_nav_trg,"inside",ordinals or 1,text_search_unit or '')
[{user.text_search_unit}] select [<user.ordinals>] any {user.win_any_dyn_nav_trg}$: user.winax_select_text(win_any_dyn_nav_trg,"BOTH",ordinals or 1,text_search_unit or '')


[{user.text_search_unit}] select [<user.ordinals>] {user.search_dir} <user.win_nav_target>$: user.winax_select_text(win_nav_target,search_dir,ordinals or 1,text_search_unit or '')

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

format <user.formatters> [<user.ordinals>] {user.search_dir} <user.win_nav_target>$: user.winax_format_text(user.formatters, win_nav_target,search_dir,ordinals or 1)

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

format <user.formatters> <user.formatters> [<user.ordinals>] {user.search_dir} <user.win_nav_target>$:
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

replace [<user.ordinals>] {user.search_dir} <user.win_nav_target> with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_nav_target,search_dir,ordinals or 1)


# TEXT REMOVAL
delete [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_replace_text("", win_next_dyn_nav_trg,"DOWN",ordinals or 1)
delete [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_replace_text("", win_previous_dyn_nav_trg,"UP",ordinals or 1)
delete [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_replace_text("", win_inside_dyn_nav_trg,"INSIDE",ordinals or 1)
delete [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_replace_text("", win_any_dyn_nav_trg,"BOTH",ordinals or 1)

delete [<user.ordinals>] {user.search_dir} <user.win_nav_target>$:
	user.winax_replace_text("", win_nav_target,search_dir,ordinals or 1)

# EXTEND CURRENT SELECTION
	# examples spoken forms:
	#   extend after previous hippopotamus
	#	extend after next period
	#   extend before third to previous brief exponent
	#	extend next three lines
	#	expand one character
extend {user.before_or_after} [<user.ordinals>] next {user.win_next_dyn_nav_trg}$:
	user.winax_extend_selection(win_next_dyn_nav_trg,"DOWN",before_or_after,ordinals or 1)
extend {user.before_or_after} [<user.ordinals>] previous {user.win_previous_dyn_nav_trg}$:
	user.winax_extend_selection(win_previous_dyn_nav_trg,"UP",before_or_after,ordinals or 1)
extend {user.before_or_after} [<user.ordinals>] inside {user.win_inside_dyn_nav_trg}$:
	user.winax_extend_selection(win_inside_dyn_nav_trg,"INSIDE",before_or_after,ordinals or 1)
extend {user.before_or_after} [<user.ordinals>] any {user.win_any_dyn_nav_trg}$:
	user.winax_extend_selection(win_any_dyn_nav_trg,"BOTH",before_or_after,ordinals or 1)

extend {user.before_or_after} [<user.ordinals>] {user.search_dir} <user.win_nav_target>$:
	user.winax_extend_selection(win_nav_target,search_dir,before_or_after,ordinals or 1)
extend {user.search_dir} [<number_small>] {user.text_search_unit}$:
	user.winax_extend_by_unit(text_search_unit,search_dir,number_small or 1)

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
	
insert <user.constructed_text> {user.before_or_after} [<user.ordinals>] {user.search_dir} <user.win_nav_target>$:
	user.winax_insert_text(constructed_text,before_or_after,ordinals or 1,search_dir,win_nav_target)

# SELECT A RANGE 
#	select FROM either a dynamic or static search target 
#	but TO static search target only
	# example spoken forms:
	#   select from previous "there is a giant..." to PHRASE "charging at me"
	#	select from next "the movie was very..." to CHARACTER period

select from previous {user.win_previous_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_previous_dyn_nav_trg,"UP",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> previous {user.win_previous_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_previous_dyn_nav_trg,"UP",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	
select from next {user.win_next_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_next_dyn_nav_trg,"DOWN",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> next {user.win_next_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_next_dyn_nav_trg,"DOWN",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	
select from inside {user.win_inside_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_inside_dyn_nav_trg,"INSIDE",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> inside {user.win_inside_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_inside_dyn_nav_trg,"INSIDE",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	
select from any {user.win_any_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_any_dyn_nav_trg,"BOTH",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> any {user.win_any_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_any_dyn_nav_trg,"BOTH",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	

select from <user.ordinals> {user.search_dir} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_nav_target,search_dir,ordinals)
	user.winax_extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals_2 or 1)	
select from {user.search_dir} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_nav_target,search_dir,1)
	user.winax_extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals or 1)	


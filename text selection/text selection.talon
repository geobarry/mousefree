os: windows
os: windows
and mode: user.zen
-
# NOTE: In old Microsoft Word .doc documents, text is garbled when there are bullets present
# Please update to .docx; there is no way to fix this from our end

# SETTINGS
selection distance <number>: user.winax_set_selection_distance(number)

# ABOUT NAVIGATION TARGETS
# "Dynamic" navigation targets (win_fwd_dyn_nav_trg, win_bkwd_dyn_nav_trg) 
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

go {user.before_or_after} [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$:
	user.winax_go_text(win_fwd_dyn_nav_trg,"DOWN",before_or_after,ordinals or 1)
go {user.before_or_after} [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$:
	user.winax_go_text(win_bkwd_dyn_nav_trg,"UP",before_or_after,ordinals or 1)
go {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.win_nav_target>$:
	user.winax_go_text(win_nav_target,text_search_direction,before_or_after,ordinals or 1)
{user.text_search_direction} <number_small> {user.text_search_unit}$: 
	user.winax_move_by_unit(text_search_unit,text_search_direction,number_small)

go down to {user.win_fwd_dyn_nav_trg}$:
	user.winax_go_text(win_fwd_dyn_nav_trg,"DOWN","after",1)
go up to {user.win_bkwd_dyn_nav_trg}$:
	user.winax_go_text(win_bkwd_dyn_nav_trg,"UP","before",1)


# SELECTION
	# example spoken forms:
	#   select next hippopotamus
	#	select previous letter cap
	#	select next bang
	#   select third previous brief exponent
	#	select paragraph
select [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$: user.winax_select_text(win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
select [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$: user.winax_select_text(win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
select [<user.ordinals>] next <user.win_nav_target>$: user.winax_select_text(win_nav_target,"DOWN",ordinals or 1)
select [<user.ordinals>] previous <user.win_nav_target>$: user.winax_select_text(win_nav_target,"UP",ordinals or 1)
select {user.text_search_unit}$: user.winax_select_unit(text_search_unit)

# HOMOPHONE CORRECTION
	# example spoken forms:
	#	phones previous ceiling
	#	phones third next word there
phones [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$: user.winax_phones_text(win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
phones [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$: user.winax_phones_text(win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
phones [<user.ordinals>] next <user.win_nav_target>$: user.winax_phones_text(win_nav_target,"DOWN",ordinals or 1)
phones [<user.ordinals>] previous <user.win_nav_target>$: user.winax_phones_text(win_nav_target,"UP",ordinals or 1)

# FORMATTING CORRECTION
format <user.formatters> [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
format <user.formatters> [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$: user.winax_format_text(user.formatters, win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
format <user.formatters> [<user.ordinals>] next <user.win_nav_target>$: user.winax_format_text(user.formatters, win_nav_target,"DOWN",ordinals or 1)
format <user.formatters> [<user.ordinals>] previous <user.win_nav_target>$: user.winax_format_text(user.formatters, win_nav_target,"UP",ordinals or 1)

format <user.formatters> <user.formatters> [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
	user.winax_format_text(formatters_2, win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$:
	user.winax_format_text(formatters_1, win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
	user.winax_format_text(formatters_2, win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] next <user.win_nav_target>$:
	user.winax_format_text(formatters_1, win_nav_target,"DOWN",ordinals or 1)
	user.winax_format_text(formatters_2, win_nav_target,"DOWN",ordinals or 1)
format <user.formatters> <user.formatters> [<user.ordinals>] previous <user.win_nav_target>$:
	user.winax_format_text(formatters_1, win_nav_target,"UP",ordinals or 1)
	user.winax_format_text(formatters_2, win_nav_target,"UP",ordinals or 1)


# TEXT REPLACEMENT
replace [<user.ordinals>] next {user.win_fwd_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_fwd_dyn_nav_trg,"DOWN",ordinals or 1)
replace [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg} with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_bkwd_dyn_nav_trg,"UP",ordinals or 1)
replace [<user.ordinals>] next <user.win_nav_target> with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_nav_target,"DOWN",ordinals or 1)
replace [<user.ordinals>] previous <user.win_nav_target> with <user.constructed_text>$:
	user.winax_replace_text(constructed_text, win_nav_target,"UP",ordinals or 1)


# EXTEND CURRENT SELECTION
	# examples spoken forms:
	#   extend after previous hippopotamus
	#	extend after next period
	#   extend before third to previous brief exponent
	#	extend next three lines
extend {user.before_or_after} [<user.ordinals>] next {user.win_fwd_dyn_nav_trg}$:
	user.winax_extend_selection(win_fwd_dyn_nav_trg,"DOWN",before_or_after,ordinals or 1)
extend {user.before_or_after} [<user.ordinals>] previous {user.win_bkwd_dyn_nav_trg}$:
	user.winax_extend_selection(win_bkwd_dyn_nav_trg,"UP",before_or_after,ordinals or 1)
extend {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.win_nav_target>$:
	user.winax_extend_selection(win_nav_target,text_search_direction,before_or_after,ordinals or 1)
extend {user.text_search_direction} [<number_small>] {user.text_search_unit}$:
	user.winax_extend_by_unit(text_search_unit,text_search_direction,number_small or 1)
extend right$: user.winax_expand_selection(false,true)
extend left$: user.winax_expand_selection(true,false)
expand [<number_small>] {user.text_search_unit}$: user.winax_expand_selection(true,true,text_search_unit or "character",number_small or 1)


# SELECT A RANGE 
#	select FROM either a dynamic or static search target 
#	but TO static search target only
	# example spoken forms:
	#   select from previous "there is a giant..." to PHRASE "charging at me"
	#	select from next "the movie was very..." to CHARACTER period

select from previous {user.win_bkwd_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_bkwd_dyn_nav_trg,"UP",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> previous {user.win_bkwd_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_bkwd_dyn_nav_trg,"UP",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	
select from next {user.win_fwd_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_fwd_dyn_nav_trg,"DOWN",1)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals or 1)	
select from <user.ordinals> next {user.win_fwd_dyn_nav_trg} to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_fwd_dyn_nav_trg,"DOWN",ordinals)
	user.winax_extend_selection(win_nav_target,"DOWN","AFTER",ordinals_2 or 1)	
select from <user.ordinals> {user.text_search_direction} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_nav_target,text_search_direction,ordinals)
	user.winax_extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals_2 or 1)	
select from {user.text_search_direction} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.winax_select_text(win_nav_target,text_search_direction,1)
	user.winax_extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals or 1)	

-
# a subset of text selection.talon available without windows accessibility text pattern
# NAVIGATION
	# example spoken forms:
	#   go before next hippopotamus
	#	go after second previous letter cap
	#	up four lines
	#	down two paragraphs

go {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.win_nav_target>$:
	user.go_text(win_nav_target,text_search_direction,before_or_after,ordinals or 1)
{user.text_search_direction} <number_small> {user.text_search_unit}$: 
	user.move_by_unit(text_search_unit,text_search_direction,number_small)


# SELECTION
	# example spoken forms:
	#   select next hippopotamus
	#	select previous letter cap
	#	select next bang
	#   select third previous brief exponent
	#	select unit paragraph
select [<user.ordinals>] next <user.win_nav_target>$: user.select_text(win_nav_target,"DOWN",ordinals or 1)
select [<user.ordinals>] previous <user.win_nav_target>$: user.select_text(win_nav_target,"UP",ordinals or 1)
select {user.text_search_unit}$: user.select_unit(text_search_unit)

# HOMOPHONE CORRECTION
	# example spoken forms:
	#	phones previous ceiling
	#	phones third next word there
phones [<user.ordinals>] next <user.win_nav_target>$: user.phones_text(win_nav_target,"DOWN",ordinals or 1)
phones [<user.ordinals>] previous <user.win_nav_target>$: user.phones_text(win_nav_target,"UP",ordinals or 1)

# FORMATTING CORRECTION
[format] <user.formatters> [<user.ordinals>] next <user.win_nav_target>$: user.format_text(user.formatters, win_nav_target,"DOWN",ordinals or 1)
[format] <user.formatters> [<user.ordinals>] previous <user.win_nav_target>$: user.format_text(user.formatters, win_nav_target,"UP",ordinals or 1)

# TEXT REPLACEMENT
replace [<user.ordinals>] next <user.win_nav_target> with <user.prose>$: user.replace_text(prose, win_nav_target,"DOWN",ordinals or 1)
replace [<user.ordinals>] previous <user.win_nav_target> with <user.prose>$: user.replace_text(prose, win_nav_target,"UP",ordinals or 1)

# EXTEND CURRENT SELECTION
	# examples spoken forms:
	#   extend after previous hippopotamus
	#	extend after next period
	#   extend before third to previous brief exponent
	#	extend next three lines
extend {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.win_nav_target>$:
	user.extend_selection(win_nav_target,text_search_direction,before_or_after,ordinals or 1)
extend {user.text_search_direction} [<number_small>] {user.text_search_unit}$:
	user.extend_by_unit(text_search_unit,text_search_direction,number_small or 1)

# SELECT A RANGE 
#	*doesn't use dynamic search so "word" or "phrase" are needed
#	 and misinterpretations are more likely
	# examples spoken forms:
	#   select from previous word rhinoceros to phrase charging at me
	#	select from next phrase the movie was very to period

select from <user.ordinals> {user.text_search_direction} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.select_text(win_nav_target,text_search_direction,ordinals)
	user.extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals_2 or 1)	
select from {user.text_search_direction} <user.win_nav_target> to [<user.ordinals>] <user.win_nav_target>$:
	user.select_text(win_nav_target,text_search_direction,1)
	user.extend_selection(win_nav_target_2,"DOWN","AFTER",ordinals or 1)	

os: windows
-
test backward search: user.test_backward_search()
test forward search: user.test_forward_search()

# SELECTION

select {user.dynamic_text_selection}:
	user.select_text(dynamic_text_selection,"both",1)

select [<user.ordinals>] {user.text_search_direction} <user.navigation_target>$: user.select_text(navigation_target,text_search_direction,ordinals or 1)
	# example spoken forms:
	#   select next hippopotamus
	#   select third previous brief exponent

select from <user.ordinals> {user.text_search_direction} <user.navigation_target> to [<user.ordinals>] <user.navigation_target>$:
	user.select_text(navigation_target,text_search_direction,ordinals)
	user.extend_selection(navigation_target_2,"DOWN","AFTER",ordinals_2 or 1)	
select from {user.text_search_direction} <user.navigation_target> to [<user.ordinals>] <user.navigation_target>$:
	user.select_text(navigation_target,text_search_direction,1)
	user.extend_selection(navigation_target_2,"DOWN","AFTER",ordinals or 1)	

extend {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.navigation_target>$:
	user.extend_selection(navigation_target,text_search_direction,before_or_after,ordinals or 1)
	# examples spoken forms:
	#   extend after next hippopotamus
	#   extend before third to previous brief exponent

go {user.before_or_after} [<user.ordinals>] {user.text_search_direction} <user.navigation_target>$:
	user.go_text(navigation_target,text_search_direction,before_or_after,ordinals or 1)

{user.text_search_direction} <number_small> {user.text_search_unit}$: 
	user.move_by_unit(text_search_unit,text_search_direction,number_small)

#select {user.text_search_unit}$: user.select_unit(text_search_unit)
extend {user.text_search_direction} <number_small> {user.text_search_unit}$:
	user.extend_by_unit(text_search_unit,text_search_direction,number_small)
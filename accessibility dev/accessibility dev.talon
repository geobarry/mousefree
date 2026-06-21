os: windows
-
# RESULTS ARE REPORTED IN TALON LOG
report mouse location: user.report_mouse_location()

# RESULTS ARE COPIED TO CLIPBOARD FOR PASTING INTO SPREADSHEET
^copy focused element information$: user.copy_focused_element_to_clipboard()
^copy registered element information$: user.copy_registered_element_to_clipboard()



^copy focused element {user.element_property} sequence$: user.copy_focused_element_sequence(element_property)
^copy focused element {user.element_property} and {user.element_property} sequence$:
	user.copy_focused_element_sequence("{element_property},{element_property_2}")
^copy mouse element information$: user.copy_mouse_elements_to_clipboard()
^copy {user.nav_key} element information$: user.copy_elements_accessible_by_key(nav_key)
^copy {user.nav_key} <number> elements$: user.copy_elements_accessible_by_key(nav_key,number,false)

# DESCENDANTS
^copy focused element [level <number>] descendants$: user.copy_element_descendants("focused",0,number or 5)
^copy focused element parent [level <number>] descendants$: user.copy_element_descendants("focused",1,number or 5)
^copy focused element grandparent [level <number>] descendants$: user.copy_element_descendants("focused",2,number or 5)
^copy focused element great grandparent [level <number>] descendants$: user.copy_element_descendants("focused",3,number or 5)
^copy focused element siblings$: user.copy_element_descendants("focused",1,1)

^copy mouse element [level <number>] descendants: user.copy_element_descendants("mouse",0,number or 5)
^copy mouse element parent [level <number>] descendants$: user.copy_element_descendants("mouse",1,number or 5)
^copy mouse element grandparent [level <number>] descendants$: user.copy_element_descendants("mouse",2,number or 5)
^copy mouse element great grandparent [level <number>] descendants$: user.copy_element_descendants("mouse",3,number or 5)
^copy mouse element siblings$: user.copy_element_descendants("mouse",1,1)

# ANCESTOR SEQUENCES
^copy focused element {user.element_property} {user.element_property} and {user.element_property} sequence$:
	user.copy_focused_element_sequence("{element_property},{element_property_2},{element_property_3}")
^copy mouse element {user.element_property} sequence$: user.copy_mouse_element_sequence(element_property)
^copy mouse element {user.element_property} and {user.element_property} sequence$:
	user.copy_mouse_element_sequence("{element_property},{element_property_2}")
^copy mouse element {user.element_property} {user.element_property} and {user.element_property} sequence$:
	user.copy_mouse_element_sequence("{element_property},{element_property_2},{element_property_3}")	

# DESCENDANT SEQUENCES
^copy focused element descendent sequences: user.copy_focused_element_descendant_sequences()

# ANCESTOR LISTS
^copy focused element ancestors$: user.copy_focused_element_ancestors()
^copy mouse element ancestors$: user.copy_mouse_element_ancestors()
^copy verbose focused element ancestors$: user.copy_focused_element_ancestors(true)
^copy verbose mouse element ancestors$: user.copy_mouse_element_ancestors(true)
^copy all element information$: user.copy_elements_to_clipboard()
^copy verbose all element information$: user.copy_elements_to_clipboard(true)
^copy level <number> element information$: user.copy_elements_to_clipboard(number)
^copy verbose level <number> element information$: user.copy_elements_to_clipboard(number,true)
^copy level <number> element deep information:
	user.copy_elements_to_clipboard(number,false,false)

# GENERAL DEBUGGING
debug current: user.debug_app_window("USER DEBUG")
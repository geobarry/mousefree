os: windows
-
# RESULTS ARE REPORTED IN TALON LOG
report mouse location: user.report_mouse_location()

# RESULTS ARE COPIED TO CLIPBOARD FOR PASTING INTO SPREADSHEET
^copy focused element information$: user.copy_focused_element_to_clipboard()
^copy registered element information$: user.copy_registered_element_to_clipboard()
^copy focused element descendants$: user.copy_focused_element_descendants()
^copy focused element ancestors$: user.copy_focused_element_ancestors()
^copy focused element {user.element_property} sequence$: user.copy_focused_element_sequence(element_property)
^copy focused element {user.element_property} and {user.element_property} sequence$:
	user.copy_focused_element_sequence("{element_property},{element_property_2}")
^copy mouse element information$: user.copy_mouse_elements_to_clipboard()
^copy {user.nav_key} element information$: user.copy_elements_accessible_by_key(nav_key)
^copy {user.nav_key} <number> elements$: user.copy_elements_accessible_by_key(nav_key,number,false)

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
^copy mouse element descendants: user.copy_mouse_element_descendants()

# ANCESTOR LISTS
^copy mouse element ancestors$: user.copy_mouse_element_ancestors()
^copy verbose focused element ancestors$: user.copy_focused_element_ancestors(true)
^copy verbose mouse element ancestors$: user.copy_mouse_element_ancestors(true)
^copy all element information$: user.copy_elements_to_clipboard()
^copy level <number> element information$: user.copy_elements_to_clipboard(number)
^copy level <number> element deep information:
	user.copy_elements_to_clipboard(number,false)

# GENERAL DEBUGGING
debug current: user.debug_app_window("USER DEBUG")
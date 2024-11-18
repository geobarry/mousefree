os: windows
-
# results are reported in talon log
report mouse location: user.report_mouse_location()

# results are copied to clipboard for pasting into spreadsheet
^copy focused element information$: user.copy_focused_element_to_clipboard()
^copy focused element descendants$: user.copy_focused_element_descendants()
^copy focused element ancestors$: user.copy_focused_element_ancestors()
^copy focused element {user.element_property} sequence$: user.copy_focused_element_sequence(element_property)
^copy focus element {user.element_property} and {user.element_property} sequence$:
	user.copy_focused_element_sequence("{element_property},{element_property_2}")
	
^copy mouse element ancestors$: user.copy_mouse_element_ancestors()
^copy verbose focused element ancestors$: user.copy_focused_element_ancestors(true)
^copy verbose mouse element ancestors$: user.copy_mouse_element_ancestors(true)
^copy all element information$: user.copy_elements_to_clipboard()
^copy level <number> element information$: user.copy_elements_to_clipboard(number)
^copy level <number> element deep information:
	user.copy_elements_to_clipboard(number,false)
^copy mouse element information$: user.copy_mouse_elements_to_clipboard()
^copy {user.nav_key} element information$: user.copy_elements_accessible_by_key(nav_key)


# Automated methods for modern windows applications like MS Office
# results are copied to clipboard for pasting into talon list file
^copy ribbon headings$: user.copy_ribbon_headings_as_talon_list()
#   ribbon heading must be selected (with black rectangle) and ribbon expanded before running following command:
^copy ribbon elements$: user.copy_ribbon_elements_as_talon_list()

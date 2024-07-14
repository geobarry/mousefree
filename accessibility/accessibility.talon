os: windows
-
# This module contains useful commands for generic situations
# COMMANDS USING DYNAMIC CAPTURES
^(element click|click on) {user.dynamic_children}$: user.click_element_by_name(dynamic_children)
^[element] hover {user.dynamic_children}$: user.hover_element_by_name(dynamic_children)
^element select {user.dynamic_children}$: user.select_element_by_name(dynamic_children)
^[element] highlight {user.dynamic_children}$: user.highlight_elements_by_name(dynamic_children)

# COMMANDS SEARCHING FOR SPECIFIC WORDS OR LETTERS
^click word <user.word>$: user.click_element_by_name(word)
^click letter <user.letter>$: user.click_element_by_name(letter,1)

# COMMANDS TO NAVIGATE TO A TARGET USING KEYS
^{user.nav_key} until <user.ax_target>$:
	key("{nav_key}")
	user.key_to_elem_by_val(nav_key,"{ax_target}.*","name",20)
	
# HIGHLIGHTS
click focused element: user.click_focused()
hover focused element: user.hover_focused()
clear highlights: user.clear_highlights()
highlight focused element: user.highlight_focused()
^{user.nav_key} highlight$:
	user.clear_highlights()
	key("{nav_key}")
	user.highlight_focused()

# COMMANDS FOR INVESTIGATING ACCESSIBILITY ELEMENTS FOR CREATING MORE COMMANDS
report mouse location: user.report_mouse_location()
copy accessible: user.copy_accessible_elements_to_clipboard()
^copy focused element information$: user.copy_focused_element_to_clipboard()
^copy focused element with children$: user.copy_focused_element_with_children(1)
^copy focused element with grandchildren$: user.copy_focused_element_with_children(2)
^copy focused element with great grandchildren$: user.copy_focused_element_with_children(3)
^copy focused element with <number> generations$: user.copy_focused_element_with_children(number)
^copy focused element ancestors$: user.copy_focused_element_ancestors()
^copy verbose focused element ancestors$: user.copy_focused_element_ancestors(12,true)
^copy enabled element information$: user.copy_enabled_element_to_clipboard()
^copy clickable element information$: user.copy_clickable_element_to_clipboard()
^copy keyboard element information$: user.copy_keyboard_element_to_clipboard()
^copy all element information$: user.copy_elements_to_clipboard()
^copy level <number> element information$: user.copy_elements_to_clipboard(number)
^copy mouse element information$: user.copy_mouse_elements_to_clipboard()
^copy selected element information$: user.copy_selected_elements_to_clipboard()
^copy {user.nav_key} element information$: user.copy_elements_accessible_by_key(nav_key)
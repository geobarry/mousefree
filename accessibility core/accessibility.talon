os: windows
os: windows
and mode: user.zen
-
# Useful accessibility commands for generic situations
# Actions include "click on","hover","highlight","label","go select","invoke"; see <user interface actions.talon-list>

# SEARCH FOR UI ELEMENT DYNAMICALLY
# Searches for a UI element with a name beginning with the spoken form
^dynamic {user.ui_action} {user.dynamic_element}$: user.act_on_named_element(dynamic_element,ui_action)

# CURRENT ELEMENTS
^{user.ui_action} focused [element]$: user.act_on_focused_element(ui_action) 
^{user.ui_action} mouse [element]$: user.act_on_mouse_element(ui_action) 

# NAVIGATE TO A TARGET USING KEYS
# Presses the designated navigation key until an element beginning with the target name is reached.
# user.nav_key includes things like tab, arrow keys, f6
# user.lazy_target is any spoken word or phrase, optionally prefixed with 'word' or 'phrase', or else characters letters numbers etc with the appropriate prefix.
^[{user.ui_action}] <user.nav_key> until [<user.ordinals>] <user.lazy_target>$:
	user.key_to_elem_by_val(nav_key,"{lazy_target}.*","name",ordinals or 1,200,'',0.03,ui_action or '')
^[{user.ui_action}] <user.nav_key> includes [<user.ordinals>] <user.lazy_target>$:
	user.key_to_elem_by_val(nav_key,".*{lazy_target}.*","name",ordinals or 1,200,'',0.03,ui_action or '')

stop [(it|repeating)]:
	user.stop_repeating()
	user.terminate_traversal()

# SCROLLING
scroll (element|item) to top: user.scroll_el_to_top()


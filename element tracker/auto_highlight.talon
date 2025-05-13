os: windows
mode: command
mode: user.zen
-

# AUTOMATIC HIGHLIGHTING AND LABELLING
auto highlight [on]: user.auto_highlight(true)
auto highlight off: user.auto_highlight(false)
auto label [on]: user.auto_label(true)
auto label off: user.auto_label(false)
clear (highlights|labels): user.clear_highlights()
reset element tracker: user.reset_tracker()

# commands to manually highlight or label focused element or mouse element 
# are located in accessibility.talon
# (basically just "(highlight|label) (focused|mouse) [element]"

# ELEMENT MARKING
# use to mark an element to retrieve or act upon later; note that you must check that element still exists
mark focused element: user.mark_focused_element()
clear marks: user.clear_marked()


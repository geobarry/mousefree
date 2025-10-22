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
refresh highlight:
	user.auto_highlight(true)
	user.auto_highlight(true)

# commands to manually highlight or label focused element or mouse element 
# are located in accessibility.talon
# (basically just "(highlight|label) (focused|mouse) [element]"

# ELEMENT MARKING
# use to mark an element to retrieve or act upon later; note that you must check that element still exists
mark focused element: user.mark_focused_element()
clear marks: user.clear_marked()

# ACCESSIBILITY MANAGEMENT: USE WITH CAUTION
# MouseFree utilizes a system to prevent accessibility stalls that prevents attempted retrieval of accessibility elements when another retrieval is believed to be in process. This system is fragile and can sometimes got stuck in a situation where it cannot perform any actions because a retrieval was never completed. The following command resets the retrieval monitor. Be aware that attempting a retrieval when another retrieval is in process is a common cause of the entire system stalling, sometimes requiring a reboot of windows.
reset retrieval: user.set_winax_retrieving(false)
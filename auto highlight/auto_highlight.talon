os: windows
-
auto highlight [on]: user.auto_highlight(true)
auto highlight off: user.auto_highlight(false)
auto label [on]: user.auto_label(true)
auto label off: user.auto_label(false)
clear (highlights|labels): user.clear_highlights()
# commands to manually highlight or label focused element or mouse element 
# are located in accessibility.talon
# (basically just "(highlight|label) (focused|mouse) [element]"

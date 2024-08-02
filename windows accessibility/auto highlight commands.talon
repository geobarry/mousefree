os: windows
and tag:user.ax_auto_highlight
-
{user.action_key}:
	key(action_key)
	user.clear_highlights()
[(go|press)] {user.nav_key}: 
	key(nav_key)
	user.act_on_focused_element("highlight")

# changing windows
window close: 
	app.window_close()
	user.clear_highlights()
window hide: 
	app.window_hide()
	user.clear_highlights()
focus <user.running_applications>: 
	user.switcher_focus(running_applications)
	user.clear_highlights()
focus$: 
	user.switcher_menu()
	user.clear_highlights()
focus last: 
	user.switcher_focus_last()
	user.clear_highlights()

# scrolling in Microsoft Edge
scroll up a little$: user.auto_highlight_scroll(-100)
scroll down a little$: user.auto_highlight_scroll(100)
scroll up$: user.auto_highlight_scroll(-200)
scroll down$: user.auto_highlight_scroll(200)
scroll up a lot$: user.auto_highlight_scroll(-300)
scroll down a that$: user.auto_highlight_scroll(300)


scroll to the top: 
	edit.file_start()
	user.clear_highlights()
scroll to the bottom: 
	edit.file_end()
	user.clear_highlights()

# more descriptive versions of common commands
[go] {user.nav_key} [(down|up|over)] to (the [<user.ordinals>] <user.ax_target> (control|button|textbox|combo box|item|layer|element|folder|command)|<user.ax_target>)$:
	key("{nav_key}")
	user.key_to_elem_by_val(nav_key,"{ax_target}.*","name",ordinals or 1)
	user.jiggle(nav_kay)
go (over|down) to <user.ax_target>:
	key("tab")
	user.key_to_elem_by_val("tab","{ax_target}.*","name")
go (back|up) to <user.ax_target>:
	key("shift-tab")
	user.key_to_elem_by_val("shift-tab","{ax_target}.*","name")
type <user.text>: insert(text)
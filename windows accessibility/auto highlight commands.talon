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

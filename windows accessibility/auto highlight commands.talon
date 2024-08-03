os: windows
and tag:user.ax_auto_highlight
os: windows
and mode:user.zen
# maybe some of these should be moved to "zen mode.py"
-
# COMMON KEY PRESSES
{user.action_key}: user.key_highlight(action_key,true,0.5)
[(go|press)] {user.nav_key}: 
	key(nav_key)
	sleep(0.5)
	user.act_on_focused_element("highlight")

# WINDOW MANAGEMENT
Close (this|the current) window: 
	app.window_close()
	user.clear_highlights()
Hide (this|the current) window: 
	app.window_hide()
	user.clear_highlights()
Switch to <user.running_applications>: 
	user.switcher_focus(running_applications)
	user.clear_highlights()
Switch application$: 
	user.switcher_menu()
	user.clear_highlights()
Switch to the (last|previous) application: 
	user.switcher_focus_last()
	user.clear_highlights()

# SCROLLING
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

# TAB SEEKING
[go] {user.nav_key} [(down|up|over)] to (<user.ax_target> | the [<user.ordinals>] <user.ax_target> (control|button|textbox|combo box|item|layer|element|folder|command))$:
	key("{nav_key}")
	user.key_to_elem_by_val(nav_key,"{ax_target}.*","name",ordinals or 1)
	user.jiggle(nav_key)
go (over|down) to <user.ax_target>:
	key("tab")
	user.key_to_elem_by_val("tab","{ax_target}.*","name")
go (back|up) to <user.ax_target>:
	key("shift-tab")
	user.key_to_elem_by_val("shift-tab","{ax_target}.*","name")

# TAB MANAGEMENT
Open a new tab: 
	app.tab_open()
	user.clear_highlights()
Switch to the (last|previous) tab: 
	app.tab_previous()
	user.clear_highlights()
Switch to the next tab: 
	user.clear_highlights()
	app.tab_next()
Close (this|the current) tab: 
	user.tab_close_wrapper()
	user.clear_highlights()
(Reopen | Restore) the (last|previous) tab: 
	user.clear_highlights()
	app.tab_reopen()
Switch to the <user.ordinals> tab: 
	user.clear_highlights()
	user.tab_jump(ordinals)
Switch to the final tab: 
	user.clear_highlights()
	user.tab_final()
(Duplicate | Clone) (this|the current) tab: 
	user.clear_highlights()
	user.tab_duplicate()

# REPETITION
again:
    core.repeat_partial_phrase(number_small or 1)
	user.clear_highlights()
# TEXT INSERTION
# should expand this to allow formatters...
type <user.text>: insert(text)
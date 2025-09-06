os: windows
-
focus <user.win_nav_target>: 
	user.app_switch_by_title("{win_nav_target}.*")
focus include <user.win_nav_target>:
	user.app_switch_by_title(".*{win_nav_target}.*")
window close <user.running_applications>:
	user.switcher_focus(running_applications)
	app.window_close()

# FOCUS
refocus: user.slow_key_press("alt:down tab left alt:up",0.1)

# special command to focus on an explorer windows since windows has so many
focus explorer: user.focus_explorer()
focus outlook: user.focus_outlook()
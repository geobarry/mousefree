os: windows
-
# Miscellaneous utilities for dealing with MS Windows OS

# FOCUS ON WINDOW BY TITLE

# by starting word or phrase, e.g. if a MS Word window has the title "community center proposal":
#    "focus word proposal" <- search by first word
#    "focus phrase community center" <- searched by first phrase

focus <user.explicit_target>: 
	user.app_switch_by_title("{explicit_target}.*")
	
# by any word or phrase, e.g.:
#    "focus include word proposal"

focus include <user.explicit_target>:
	user.app_switch_by_title(".*{explicit_target}.*")

# CLOSE WINDOW THAT IS NOT IN FOCUS
window close <user.running_applications>:
	user.switcher_focus(running_applications)
	app.window_close()

# SOMETIMES IT IS USEFUL TO FOCUS ON ANOTHER WINDOW THEN BRING FOCUS BACK TO CURRENT WINDOW
refocus: user.slow_key_press("alt:down tab left alt:up",0.2)

# APPS THAT ARE NOTORIOUS FOR FOCUSING ON HIDDEN WINDOWS
focus explorer: user.focus_explorer()
focus outlook: user.focus_outlook()

# TASK BAR
safely remove hardware: user.invoke_taskbar_item("Safely Remove Hardware.*")
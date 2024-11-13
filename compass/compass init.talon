compass <user.bearing>$:
	user.compass_set_bearing(user.bearing)
	mode.enable("user.compass")
	mode.disable("command")
compass display [mode] {user.compass_display_mode}:
	user.compass_enable()
	mode.enable("user.compass") 
	user.compass_set_display_mode(compass_display_mode)
# move the mouse around a little
compass jiggle:
	user.compass_jiggle()
	user.compass_enable(1)
	mode.enable("user.compass") 
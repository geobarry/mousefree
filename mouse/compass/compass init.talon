compass <user.bearing>$: user.compass_enable(bearing)
compass display [mode] {user.compass_display_mode}:
	user.compass_enable(-999,compass_display_mode)
# move the mouse around a little

compass jiggle:
	print("attempting compass jiggle")
	user.compass_jiggle()

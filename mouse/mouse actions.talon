os: windows
mode: command
or mode: user.compass
-
mouse to screen [{user.handle_position}]:
	user.mouse_to_screen_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to [focused] element [{user.handle_position}]:
	user.mouse_to_focused_element_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to window [{user.handle_position}]:
	user.mouse_to_active_window_handle(handle_position or "center")
	user.compass_enable(0,1)
^pan <user.bearing>$:
	print("{bearing}")
	user.drag_window_center(bearing,500)
(mouse|compass) jiggle: user.compass_jiggle()
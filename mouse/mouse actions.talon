os: windows
mode: command
mode: user.compass
-
mouse to screen [{user.handle_position}]:
	user.mouse_to_screen_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to element [{user.handle_position}]:
	user.mouse_to_focused_element_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to window [{user.handle_position}]:
	user.mouse_to_active_window_handle(handle_position or "center")
	user.compass_enable(0,1)
(mouse|compass) jiggle: user.compass_jiggle()
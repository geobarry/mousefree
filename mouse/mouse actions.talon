os: windows
mode: command
mode: user.compass
mode: user.zen
-
mouse to screen [{user.handle_position}]:
	user.mouse_to_screen_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to [focused] element [{user.handle_position}]:
	user.mouse_to_focused_element_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to marked element [{user.handle_position}]:
	user.mouse_to_marked_element_handle(handle_position or "center")
	user.compass_enable(0,1)
mouse to window [{user.handle_position}]:
	user.mouse_to_active_window_handle(handle_position or "center")
	user.compass_enable(0,1)
^pan <user.bearing> [<number>]$:
	print("{bearing}")
	user.drag_window_center(bearing,number or 500)
(mouse|compass) jiggle: user.compass_jiggle()

# ADDITIONAL WHEEL MOVEMENT
wheel up element:
	user.mouse_to_focused_element_handle(handle_position or "center")
	user.mouse_scroll_up()
wheel down element:
	user.mouse_to_focused_element_handle(handle_position or "center")
	user.mouse_scroll_down()
# EXPERIMENTAL
get screen bounds: user.get_screen_bounds()
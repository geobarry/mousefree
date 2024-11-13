os: windows
mode: command
mode: user.compass
-
mouse to screen {user.handle_position}:
	user.mouse_to_screen_handle(handle_position)
	user.eagle_enable(1)
	mode.enable("user.compass") 
mouse to element {user.handle_position}:
	user.mouse_to_focused_element_handle(handle_position)
	user.eagle_enable(1)
	mode.enable("user.compass") 

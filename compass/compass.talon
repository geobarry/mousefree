mode: user.compass
-
# TURN OFF COMPASS; WILL ALSO TURN OFF AUTOMATICALLY WITH MOST MOUSE COMMANDS, AFTER DELAY
(exit compass|stop it): user.compass_disable()

# SET DIRECTION
# set the compasss direction, e.g. "north"

[compass] <user.bearing>$:	user.compass_enable(user.bearing)

# ROTATE
# rotate compass towards a compass direction, e.g. "30 east"

[compass] <user.real_number> [degrees] <user.bearing>$: user.move_cardinal(real_number, user.bearing)
nudge <user.bearing>$: user.move_cardinal(0.3,user.bearing)

# reverse direction  
[compass] reverse$: user.reverse()

# MOVE
# move specified distance in pixels, e.g. "go five hundred"
go <number>$: user.fly_out(number,500)
move <number>$: user.fly_out(number,1000)
walk <number>$: user.fly_out(number,3000)
crawl <number>$: user.fly_out(number,8000)

# move backwards specified distance in pixels, e.g. "backup fifty"
backup <number>$: user.fly_back(number)

# MOUSE COMMANDS THAT WILL NOT EXIT COMPASS
drag: user.mouse_drag(0)

# MOUSE COMMANDS THAT WILL EXIT COMPASS
(touch | click):
	mouse_click(0)
	user.compass_enable(-999,1)
(righty | right click):
	mouse_click(1)
	user.compass_enable(-999,1)
drag end:
    user.mouse_drag_end()
	user.compass_enable(-999,1)
(double click | dub click | duke):
	mouse_click() 
	mouse_click()
	user.compass_enable(-999,1)
wheel down: 
	user.mouse_scroll_down()
	user.compass_enable(-999,1)
wheel tiny [down]: 
	user.mouse_scroll_down(0.2)
	user.compass_enable(-999,1)
wheel downer: 
	user.mouse_scroll_down_continuous()
	user.compass_enable(-999,1)
wheel up: 
	user.mouse_scroll_up()
	user.compass_enable(-999,1)
wheel tiny up: 
	user.mouse_scroll_up(0.2)
	user.compass_enable(-999,1)
wheel upper: 
	user.mouse_scroll_up_continuous()
	user.compass_enable(-999,1)
wheel left: 
	user.mouse_scroll_left()
	user.compass_enable(-999,1)
wheel tiny left: 
	user.mouse_scroll_left(0.5)
	user.compass_enable(-999,1)
wheel right: 
	user.mouse_scroll_right()
	user.compass_enable(-999,1)
wheel tiny right: 
	user.mouse_scroll_right(0.5)
	user.compass_enable(-999,1)

# COMMANDS FOR REPEATING
second: core.repeat_command(1)
again: core.repeat_partial_phrase(1)

# COMMAND FOR DEBUGGING WHILE IN COMPASS MODE
^talon test last$:
    phrase = user.history_get(1)
    user.talon_sim_phrase(phrase)

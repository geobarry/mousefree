tag: user.eagle_showing
-
# Commands for when eagle is open but is not active
# Eagle remains active for about 10-20 seconds after each previous command
# For shorter commands while eagle is active, see eagle_active.talon

# Note: For me "eagle" often misheard as "head go", ergo 
# attempt to catch that by including both options in each command
# This is not really pretty, looking for a better solution

# SHUT DOWN EAGLE
(eagle off|eagle laugh|eagle out|grid off):
	user.eagle_disable()

# CHANGE DISPLAY MODE
eagle display {user.eagle_display_modes}:
	user.display_mode(user.eagle_display_modes)
	
# SET DIRECTION
# set the movement direction to a compasss direction, e.g. 'north-northeast','up'
(eagle|head go) <user.bearing>:	user.set_cardinal(user.bearing)
# reverse direction  
(eagle|head go) reverse: user.reverse()

# ROTATE
# rotate compass bearing towards a compass direction, e.g. '30 (east|right)'
(eagle|head go) <number> <user.bearing>: user.move_cardinal(number, user.bearing)
(eagle|head go) <user.ordinals> <user.bearing>: user.move_cardinal(ordinals,user.bearing)
(eagle|head go) nudge <user.bearing>: user.move_cardinal(0.3,user.bearing)

# MOVE
# move specified distance in pixels, e.g. '(jump|fly|walk|crawl) five hundred'
(eagle|head go) jump <number>: user.fly_out(number,10)
(eagle|head go) fly <number>: user.fly_out(number,1000)
(eagle|head go) walk <number>: user.fly_out(number,3000)
(eagle|head go) crawl <number>: user.fly_out(number,8000)

# move backwards specified distance in pixels
(eagle|head go) (back|backup) <number>: user.fly_back(number)
	
# CATCH COMMON SPEECH MISRECOGNITION ('fly' heard as 'five')
(eagle|head go) <user.number_string>: user.five_fly_out(number_string)
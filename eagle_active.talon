os: windows
tag: user.eagle_active
-
# Shortcut commands where "eagle" doesn't need to be spoken
# Active for about 10-20 seconds after last previous command


# SET DIRECTION
# set the movement direction to a compasss direction, e.g. 'north-northeast','up'
<user.bearing>:	user.eagle_set_bearing(user.bearing)
# reverse direction  
reverse: user.reverse()

# ROTATE
# rotate compass bearing towards a compass direction, e.g. '30 (east|right)'
<number> [degrees] <user.bearing>: user.move_cardinal(number, user.bearing)
<user.ordinals> <user.bearing>: user.move_cardinal(ordinals,user.bearing)
nudge <user.bearing>: user.move_cardinal(0.3,user.bearing)

# MOVE
# move specified distance in pixels, e.g. '(jump|fly|walk|crawl) five hundred'
jump <number>: user.fly_out(number,10)
(fly|five) <number>: user.fly_out(number,1000)
walk <number>: user.fly_out(number,3000)
crawl <number>: user.fly_out(number,8000)

# move backwards specified distance in pixels
backup <number>: user.fly_back(number)
	
# CATCH COMMON SPEECH MISRECOGNITION ('fly' heard as 'five')
#five <user.number_string>: user.five_fly_out(number_string)
  
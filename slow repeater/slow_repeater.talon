#precise control over repeat interval	
<user.key> <number> second repeat$:
	user.start_key_repeat("{key}",number*1000)
<user.key> <number> (tic|take) repeat$:
	user.start_key_repeat("{key}",number*100)

#short cut for common intervals
<user.key> {user.slow_repeater_speed_word} [repeat]$:
	user.start_key_repeat("{key}",slow_repeater_speed_word)

{user.slow_repeater_speed_word} repeat$:
	user.start_cmd_repeat(slow_repeater_speed_word)

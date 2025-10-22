mode: user.slow_repeating
#tag: user.slow_repeating
-

stop [(it|repeating)]:
	user.stop_repeating()
hard stop:
	user.hard_stop_repeating()
faster:
	user.repeat_faster()
slower:
	user.repeat_slower()


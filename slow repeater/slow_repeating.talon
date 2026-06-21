mode: user.slow_repeating
#tag: user.slow_repeating
-

stop [(it|repeating)]: user.stop_repeating()
hard stop: user.hard_stop_repeating()
faster$: user.repeat_change_speed(1.5)
slower$: user.repeat_change_speed(0.67)


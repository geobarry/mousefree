mode: user.zen
# This mode is designed to allow you to focus on
# a small set of general commands and then commands for a specific application
# It is recommended that you keep and mod commands sparse, and/or use
# long descriptive phrases that aren't likely to be said accidentally
# The idea is to reduced the possibility of mis recognized commands
# being accidentally fired.
-
^command mode$:
	mode.enable("command")
	mode.disable("user.zen")
# Next command reduces possibility of mis recognized commands being fired
<user.text>: user.do_nothing()
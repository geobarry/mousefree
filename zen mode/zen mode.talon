mode: user.zen

# This mode is designed to allow you to focus on
# a small set of general commands as well as commands for a specific application
# The idea is to sacrifice broad functionality 
# in order to minimize misrecognized commands.
# To avoid phonetic overlap it is recommended to keep commands sparse, and/or use
# long descriptive phrases that aren't likely to be said accidentally
-
^command mode$:
	mode.disable("user.zen")
	mode.enable("command")
# Next command prevents talon from trying to latch onto
# a command that is very different from what you say
# by giving talon another option (because talon will try to find something that matches if it can, so if there are no good matches it will latch onto an ok match)
<user.text>: user.do_nothing()
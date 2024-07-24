^fancy mode$:
	mode.enable("user.fancy_dictation")
	mode.disable("command")
	# it takes longer to think when doing dictation, so let's increase the time out to three seconds
	speech.timeout(3)

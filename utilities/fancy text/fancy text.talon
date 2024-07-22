mode: user.fancy_dictation
-
^command mode$:
    mode.disable("user.fancy_dictation")
    mode.enable("command")
	# change this to match your settings in community or the default value which I think is 0.4
	speech.timeout(1.0)


sentence <user.fancy_unit>+$: user.fancy_text(fancy_unit_list,true,false)
[phrase] <user.fancy_unit>+$: user.fancy_text(fancy_unit_list,false,false)

# EXAMPLE
# this is an example of dubstring putting something in quotes close dub string and then continuing period
# RESULT
# This is an example of "putting something in quotes" and then continuing. 

# EXAMPLE
# use other formatters to create snake python variables close snake or just upper shout loudly close upper period
# RESULT
# Use other formatters to create python_variables or just SHOUT LOUDLY. 


# EXAMPLE


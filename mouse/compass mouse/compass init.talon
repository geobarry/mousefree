# START COMPASS WITH A BEARING ANGLE, e.g.
#    Compass North
#    Compass North Northeast
#    Compass North Twenty West
compass <user.bearing>$: user.compass_enable(bearing)

# START COMPASS WITH PREVIOUS BEARING ANGLE
compass$: user.compass_enable()

# MOVE THE MOUSE AROUND A LITTLE
compass jiggle:	user.compass_jiggle()

# CHANGE THE AMOUNT OF INFORMATION SHOWN IN THE GRID LINES
compass display heavy: user.compass_enable(-999,4)
compass display medium: user.compass_enable(-999,3)
compass display light: user.compass_enable(-999,2)
compass display extra light: user.compass_enable(-999,1)
os: windows
# For snipping areas of the screen
# Needs to be updated to utilize/integrate with community
-
snip screen$: user.snip_screen()
snip window$: user.snip_window()
snip element$: user.snip_element()
snip rectangle [start]$: user.start_rect()
snip rectangle finish$: user.save_rect()
snip rectangles clear: user.clear_snip_rect()
snip <number>: user.snip_saved_rect(number-1)

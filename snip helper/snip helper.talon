os: windows
# For snipping areas of the screen
# Needs to be updated to utilize/integrate with community
-
snip screen$: user.snip_screen()
snip window$: user.snip_window()
snip [focused] element$: user.snip_element()
snip buffered element$: user.snip_element(3)
snip record [start]$: user.start_rect()
snip record finish$: user.save_rect()
snip rectangles clear: user.clear_snip_rect()
snip rectangle <number>: user.snip_saved_rect(number-1)


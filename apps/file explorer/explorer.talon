os: windows
app.exe: explorer.exe
mode: user.zen
mode: command
-
# ACTIONS ON FILES AND FOLDERS IN MAIN (FILE) PANEL

## CURRENTLY SELECTED
## Commands that perform actions on currently selected file(s) or folder(s)
##  examples:
##   "folder open"
##   "file cut"
##   "move into <name of any visible subfolder>"
##   "stash into parent folder"
##   "move/stash into <one of your named system paths>"

(file|folder) {user.explorer_action}$: user.explorer_process_item('','',explorer_action)

move into folder {user.dynamic_folder}$: user.explorer_move_to('',0,dynamic_folder,'move')
move into parent [folder]$: user.explorer_move_to('',1,'','move')
move into <user.system_path>: user.explorer_move_to(system_paths,0,'','move')
move into <user.system_path> {user.subfolder}: user.explorer_move_to("{system_path}\{subfolder}",0,'','move')

stash into folder {user.dynamic_folder}$: user.explorer_move_to('',0,dynamic_folder,'stash')
stash into parent [folder]$: user.explorer_move_to('',1,'','stash')
stash into <user.system_path>: user.explorer_move_to(system_paths,0,'','stash')
stash into <user.system_path> {user.subfolder}: user.explorer_move_to("{system_path}\{subfolder}",0,'','stash')
	
## BY SPOKEN FORM
## Commands that perform actions on files or folders designated by name
##  examples:
##   "file open <first word or first couple words of file name>"
##   "folder delete <first couple words of folder name>"

file {user.explorer_action} {user.dynamic_file}$: user.explorer_process_item(dynamic_file,"file",explorer_action)
folder {user.explorer_action} {user.dynamic_folder}$:
	user.explorer_process_item(dynamic_folder,"folder",explorer_action)
file {user.dynamic_file} move to [folder] {user.dynamic_folder}$:
	user.explorer_process_item(dynamic_file,"file","cut")
	user.explorer_process_item(dynamic_folder,"folder","open")
	sleep(0.7)
	key("ctrl-v")

# miscellaneous - needs refactoring to fit into above organization
open with {user.app}$: user.explorer_open_with(app)
{user.file_ext} {user.explorer_action} {user.dynamic_file_with_ext}$: 
	print("talon file: {dynamic_file_with_ext}")
	user.explorer_process_item(dynamic_file_with_ext,"file",explorer_action)
{user.explorer_context_option}$:
	user.explorer_context_action(explorer_context_option)

# NAVIGATION TO SYSTEM PATHS
# override default because default doesn't work consistently, leaves drop down hanging
go <user.system_path>$: user.explorer_navigate_to_folder(system_path)
# if you have a common naming convention for subfolders, create a talon list called subfolder and use the following:
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")

# these are a bit experimental
go recent: user.explorer_special_group("Recent")
go favorites: user.explorer_special_group("Favorites")
go shared: user.explorer_special_group("Shared")

# UI NAVIGATION
# Panels
panel (main|files): user.explorer_select_items_panel()
panel navigation: user.explorer_select_navigation_panel()
address bar: key(alt-d)

# Toolbar drop-downs
# These don't look like menus in other programs, but essentially they are
menu new: user.explorer_show_button_options("New")
menu sort: user.explorer_show_button_options("Sort")
menu view: user.explorer_show_button_options("View")
menu more [options]: user.explorer_show_button_options("More options")
{user.explorer_app_bar_item}: user.explorer_invoke_app_bar_item(explorer_app_bar_item)

# ALTERNATE VIEWS OF ITEMS PANEL
view large (icons|thumbnails): key(ctrl-shift-1)
view medium (icons|thumbnails): key(ctrl-shift-2)
view small (icons|thumbnails): key(ctrl-shift-3)
view list: key(ctrl-shift-4)
view (detailed|details): key(ctrl-shift-6)
view distraction free: key(ctrl-shift-5)
filter: user.explorer_filter()

# COLUMN MANAGEMENT
sort by {user.explorer_column}: user.explorer_sort_by(explorer_column)
columns show: user.explorer_manage_column()
column show {user.explorer_column}:
	user.explorer_manage_column(explorer_column,"show")
column hide {user.explorer_column}:
	user.explorer_manage_column(explorer_column,"hide")
column {user.explorer_column} wider [<number>]:
	user.explorer_manage_column(explorer_column,"sizeup",number or 50)
column {user.explorer_column} narrower [<number>]:
	user.explorer_manage_column(explorer_column,"sizedown",number or 50)



# IDIOSYNCRATIC COMMANDS
new folder: key(ctrl-shift-n)
copy full path: 
	x = user.explorer_current_path()
	clip.set_text("{x}")
copy folder:
	folder = user.explorer_current_folder()
	clip.set_text("{folder}")

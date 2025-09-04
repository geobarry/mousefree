os: windows
app.exe: explorer.exe
mode: user.zen
mode: command
-
# ACTIONS ON FILES AND FOLDERS IN MAIN (FILE) PANEL

## Actions on currently selected a file(s) or folder(s)

(file|folder) {user.explorer_action}$: user.explorer_process_item("","",explorer_action)
move to folder {user.dynamic_folder}$:
	user.explorer_select_items_panel()
	edit.cut()
	sleep(0.1)
	user.explorer_process_item(dynamic_folder,"folder","open")
	sleep(0.7)
	key("ctrl-v")
	sleep(1.0)
	key("alt-up")
move to parent [folder]$:
	user.explorer_select_items_panel()
	edit.cut()
	sleep(0.1)
	user.file_manager_open_parent()
	sleep(0.7)
	key("ctrl-v")	

## Actions on files or folders identified dynamically from file/folder names
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
# if you have a common naming convention for subfolders, create a talon list and use the following:
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")

# UI NAVIGATION
panel (items|files): user.explorer_select_items_panel()
panel navigation: user.explorer_select_navigation_panel()
[panel] address bar: key(alt-d)
copy full path: user.explorer_copy_full_path()
copy folder: user.explorer_copy_folder()
go recent: user.explorer_special_group("Recent")
go favorites: user.explorer_special_group("Favorites")
go shared: user.explorer_special_group("Shared")

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

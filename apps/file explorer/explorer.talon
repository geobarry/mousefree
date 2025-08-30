os: windows
app.exe: explorer.exe
mode: user.zen
mode: command
-
test folder: user.explorer_test()
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

new options: user.explorer_show_button_options("New")
sort options: user.explorer_show_button_options("Sort")
view options: user.explorer_show_button_options("View")
more options: user.explorer_show_button_options("More options")
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
new file:
	key(alt-up)
	sleep(0.2)
	key(enter)
	sleep(1.0)
	key(menu)
	sleep(0.2)
	key(w 1)
	sleep(0.2)
	key(up:3)
new folder: key(ctrl-shift-n)
clone window:
	key(alt-d ctrl-c super)
	sleep(0.2)
	insert("File Explorer")
	key(enter)
	sleep(0.5)
	key(super-right)
	sleep(1.5)
	key(alt-d)
	sleep(1.5)
	key(ctrl-v enter)
create animation$: 
	user.explorer_open_path_in_terminal()
	sleep(1.0)
	msg = "ffmpeg -framerate 30 -i k_%d.png -c:v libx264 -r 30 -pix_fmt yuv420p animation.mp4"
	insert(msg)
create animations from sub folders$: user.explorer_create_animations_from_subfolders()
compress video [file]$: user.compress_video_file()
start server: user.explorer_start_server()
open file locator$:
	# grab path to current folder
	key(alt-d)
	sleep(0.5)
	edit.copy()
	# launch file locator
	key(super)
	sleep(1.0)
	insert("filelocator")
	sleep(1.0)
	key(enter)
	sleep(1.5)
	# remove default file name and enter the folder path
	key(del)
	key(tab:2)
	sleep(1)
	edit.paste()
	sleep(1)
	key(shift-tab)

open jupyter [notebook]$:
	# grab path to current folder
	key(alt-d)
	sleep(0.5)
	edit.copy()
	# open the python command prompt
	key(super)
	sleep(0.5)
	insert("python command prompt")
	sleep(0.5)
	key(enter)
	sleep(2.5)
	# change directories and open jupyter notebook
	insert("cd ")
	sleep(0.5)
	edit.paste()
	sleep(0.5)
	key(enter)
	sleep(0.5)
	insert("jupyter notebook")
	key(enter)
	
process desire to learn downloads:
	user.process_desire_to_learn_downloads()
prepend <user.text>:
	key(f2)
	sleep(0.2)
	x = edit.selected_text()
	sleep(0.2)
	insert("{text} {x}")
	sleep(0.4)
	key(enter)
	sleep(0.4)
	key(home down:3)
	
test current path: print("{user.file_manager_current_path()}")
os: windows
app.exe: explorer.exe
mode: user.zen
mode: command
-

# warning: this will be in context when you don't realize it
open with notepad: user.slow_key_press("menu w n enter",0.5)

# override "open up"
file {user.explorer_action} {user.dynamic_file}$: user.explorer_process_item(dynamic_file,"file",explorer_action)
folder {user.explorer_action} {user.dynamic_folder}$:
	user.explorer_process_item(dynamic_folder,"folder",explorer_action)
open with {user.app}$: user.explorer_open_with(app)

{user.file_ext} {user.explorer_action} {user.dynamic_file_with_ext}$: 
	print("talon file: {dynamic_file_with_ext}")
	user.explorer_process_item(dynamic_file_with_ext,"file",explorer_action)

file move to {user.dynamic_folder}$:
	key("ctrl-x")
	user.explorer_process_item(dynamic_folder,"folder","open")
	sleep(0.7)
	key("ctrl-v")
file {user.dynamic_file} move to {user.dynamic_folder}$:
	user.explorer_process_item(dynamic_file,"file","cut")
	user.explorer_process_item(dynamic_folder,"folder","open")
	sleep(0.7)
	key("ctrl-v")

#(file|folder) {user.explorer_context_option}$:
#	user.explorer_context_action(explorer_context_option)


# override default because default doesn't work
go <user.system_path>$: user.explorer_navigate_to_folder(system_path)
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")

# long form for demo/zen mode
go to [the] parent folder: 
	user.file_manager_open_parent()
	user.clear_highlights()
#(panel files|go to the files panel): user.explorer_tab_to_files()
#
panel files: user.explorer_select_files_panel()

copy full path: user.file_explorer_copy_full_path()
copy folder: user.file_explorer_copy_folder()

# alternate views
view large icons: key(ctrl-shift-1)
view medium icons: key(ctrl-shift-2)
view small icons: key(ctrl-shift-3)
view list: key(ctrl-shift-4)
view (detailed|details): key(ctrl-shift-6)
view distraction free: key(ctrl-shift-5)

# column management
sort by {user.explorer_column}: user.file_explorer_sort_by(explorer_column)
columns show: user.explorer_manage_column()
column show {user.explorer_column}:
	user.explorer_manage_column(explorer_column,"show")
column hide {user.explorer_column}:
	user.explorer_manage_column(explorer_column,"hide")
column {user.explorer_column} wider [<number>]:
	user.explorer_manage_column(explorer_column,"sizeup",number or 50)
column {user.explorer_column} narrower [<number>]:
	user.explorer_manage_column(explorer_column,"sizedown",number or 50)



address bar: key(alt-d)


open with: key(menu h)
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
zip selected:
	key(menu)
	sleep(0.5)
	key(z)

replace with underscores: user.replace_with_underscores()

# very specific idiosyncratic commands
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
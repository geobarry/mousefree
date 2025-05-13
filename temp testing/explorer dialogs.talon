os: windows
and app.name: /.*(Word|Excel|PowerPoint|Edge|Outlook|Notepad|Adobe Acrobat|Python).*/
and win.title: /(Open|Save|Publish|Insert|Export).*/
-
go <user.system_path>$: user.explorer_navigate_to_folder(system_path)
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")
panel files: user.explorer_select_files_panel()
go parent: key(alt-up)
# use dynamic list to avoid misrecognitions
^file {user.explorer_action} {user.dynamic_file}$: user.explorer_process_item(dynamic_file,"file",explorer_action)
folder open {user.dynamic_folder}$:
	user.explorer_process_item(dynamic_folder,"folder","open")
debug test {user.dynamic_folder}: print(dynamic_folder)	

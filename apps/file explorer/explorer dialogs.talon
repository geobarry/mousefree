os: windows
and app.name: /.*(Word|Excel|PowerPoint|Edge|Outlook|Notepad|Adobe Acrobat|Python|Visual Studio|Triangulation_Visualization).*/
and win.title: /(Open|Save|Publish|Insert|Load|Export).*/
-
# SUBSET OF COMMON COMMANDS FROM MAIN EXPLORER APPLICATION,
# FOR APPLICATIONS THAT USE STANDARD FILE SELECTION DIALOG
go <user.system_path>$: user.explorer_navigate_to_folder(system_path)
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")
panel (items|files): user.explorer_select_items_panel()
go parent: key(alt-up)
^file {user.explorer_action} {user.dynamic_file}$: user.explorer_process_item(dynamic_file,"file",explorer_action)
folder open {user.dynamic_folder}$: user.explorer_process_item(dynamic_folder,"folder","open")
new folder: user.explorer_dialog_new_folder()


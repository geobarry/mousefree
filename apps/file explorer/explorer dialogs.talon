os: windows
and app.name: /.*(Word|Excel|PowerPoint|Edge|Outlook|Notepad|Adobe Acrobat|Python|Visual Studio|Triangulation_Visualization).*/
and win.title: /(Open|Save|Publish|Insert|Load|Export).*/
-
# SUBSET OF COMMON COMMANDS FROM MAIN EXPLORER APPLICATION,
# FOR APPLICATIONS THAT USE STANDARD FILE SELECTION DIALOG

# UI NAVIGATION
panel (items|files): user.explorer_select_items_panel()
new folder: user.explorer_dialog_new_folder()
file name: user.explorer_dialog_file_name()
file type$: user.explorer_dialog_file_type()
file type {user.file_type_description}: user.explorer_dialog_file_type(file_type_description)
button save: user.explorer_dialog_button("Save.*",false)
dialog save: user.explorer_dialog_button("Save.*",true)
button cancel: user.explorer_dialog_button("Cancel",false)
dialog cancel: user.explorer_dialog_button("Cancel",true)
button Open: user.explorer_dialog_button("Open",false)
dialog Open: user.explorer_dialog_button("Open",true)

# DIRECTORY NAVIGATION
go <user.system_path>$: user.explorer_navigate_to_folder(system_path)
go <user.system_path> {user.subfolder}$: user.explorer_navigate_to_folder("{system_path}\\{subfolder}")
go parent: key(alt-up)
folder open {user.dynamic_folder}$: user.explorer_process_item(dynamic_folder,"folder","open")

# FILE ACTIONS: open, select, cut, copy, delete
^file {user.explorer_action} {user.dynamic_file}$: user.explorer_process_item(dynamic_file,"file",explorer_action)




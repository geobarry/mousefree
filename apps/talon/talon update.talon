os: windows
and app.name: Talon
and win.title: Talon Update
os: windows
and app.exe: /^talon\.exe$/i
and win.title: Talon Update
-
Skip This Version: user.invoke_talon_update_button("Skip This Version")
Remind Me Later: user.invoke_talon_update_button("Remind Me Later")
Install Update: user.invoke_talon_update_button("Install Update")
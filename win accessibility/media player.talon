os: windows
and app.name: Application Frame Host
os: windows
and app.exe: /^applicationframehost\.exe$/i
-
(play|pause): key(ctrl-p)
skip (back|backward): key(ctrl-left)
skip forward: key(ctrl-right)
skip back <number>$: user.mp_skip(number,"backward")
skip forward <number>$: user.mp_skip(number,"forward")
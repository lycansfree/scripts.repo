rem 自动重启windows下浏览器并打开网址,自动全屏
dim ws
rem workdir, command
rem workdir=left(wscript.scriptfullname,instrrev(wscript.scriptfullname,"\")-1)
rem command = "cmd /c " + workdir + "/aaa.bat"
rem ws.run command

set ws = createobject("Wscript.Shell") 
ws.sendkeys("^{F4}") 
' ws.run "cmd /c start C:\Users\admin\AppData\Local\Google\Chrome\Application\chrome.exe --kiosk http://aiops.it.bx"
' ws.run "cmd /c start C:\Users\admin\AppData\Local\Google\Chrome\Application\chrome.exe http://wiki.it.bx/largescreen/EleventhFloor/gq.html",0,true
' wscript.sleep 1000 * 5
' ws.sendkeys("{F11}")
wscript.sleep 1000
ws.run "cmd /c start C:\Users\admin\AppData\Local\Google\Chrome\Application\chrome.exe --kiosk http://wiki.it.bx/largescreen/EleventhFloor/gq.html"

wscript.sleep 1000 * 60
ws.sendkeys("^{F5}")

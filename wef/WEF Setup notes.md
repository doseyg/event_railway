# On the Windows Event Collector Server
- winrm qc
- wecutil qc

## Configure an event subscriptiuon channel
Open eventvwr, right click on Forwarded Events, Go to properties, Click the Subscriptions tab at the top
- Click Create
- Choose Source computer initiated, and type Domain Computers
-- optionally also choose Domain Controllers, which by default are not included in Domain Computers
- Click Select Events, and then By Log 
-- Choose Windows Events
-- Choose Windows Powershell by expanding Application and Services Logs


In GPO
This goes in Computer>Policies>Admin Templates>Windows Components>Event Forwarding
Server=http://hostname:5985/wsman/SubscriptionManager/WEC,Refresh=60

dsacls “CN=AdminSDHolder,CN=System,DC=yourdomainname,DC=tld” /G “S-1-5-20:WS;Validated write to service principal name”

If you don't want to use Forwarded Events for everything

Copy the .dll and .man file to C:\Windows\system23

### Copy .man and .dll to server and run
wevtutil im c:\Windows\system32\CustomEventChannels.man

### Load .man file to C:\ECMan

Optional: To build your own custom files, run these commands

cd\ECMan
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\mc.exe" C:\ECMan\CustomEventChannels.man
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\mc.exe" -css CustomEventChannels.DummyEvent C:\ECMan\CustomEventChannels.man
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\rc.exe" C:\ECMan\CustomEventChannels.rc
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /win32res:C:\ECMan\CustomEventChannels.res /unsafe /target:library /out:C:\ECMan\CustomEventChannels.dll C:\ECMan\CustomEventChannels.cs



# On the Windows Event Collector Server
## Enable the WinRM and WEC service
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

# Enable Computers to send WEF
## Import GPO
- Create a new GPO object named WEF
- Right click on the WEF GPO and choose Import
-- You will have to fix the user and group permissions, and also adjust the WEF server URL

## Create your own GPO
Computer Configuration->Policies->Admin Templates->Windows Components->Event Forwarding
Configure the computers to use the subscritions created above
- Configure target Subscrition Manager
- click enabled
- click Show
- type this in the box, editing as approprioate: Server=http://hostname:5985/wsman/SubscriptionManager/WEC,Refresh=60

Computer Configuration->Policies->Windows Settings->Security Settings->Restricted Groups
Add the NETWORK SERVICE account to the Event Log Readers Group. 
- right click and choose Add Group
- Browse for Event Log Readers
- click Add under Members of this group
- type NETWORK SERVICE, you cannot browse for it because it is a local user, not a domain account.

Start the WinRM service
Computer Configuration>Preferences>Control Panel Settings>Services
- right click and choose new service
- set startup type to automatic delayed
- click the 3 dots by Service Name to browse to WinRM
- set the Service Action to Start Service

Link the GPO
- Right click on the root of your domain and link to an existing GPO
- choose WEF


dsacls “CN=AdminSDHolder,CN=System,DC=yourdomainname,DC=tld” /G “S-1-5-20:WS;Validated write to service principal name”

## Import custom event channles (Optional)
If you don't want to use Forwarded Events for everything, then do this

- Copy the CustomEventChannles.dll and CustomEventChannles.man file to C:\Windows\system32
- To import them run the command wevtutil im c:\Windows\system32\CustomEventChannels.man

### Create your own custom event channles (optional)
If you want some different event channels than what I created.
Edit the CustomEventChannles.man
Then to build your own custom files, run these commands

cd \ECMan
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\mc.exe" C:\ECMan\CustomEventChannels.man
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\mc.exe" -css CustomEventChannels.DummyEvent C:\ECMan\CustomEventChannels.man
"C:\Program Files (x86)\Windows Kits\8.1\bin\x64\rc.exe" C:\ECMan\CustomEventChannels.rc
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /win32res:C:\ECMan\CustomEventChannels.res /unsafe /target:library /out:C:\ECMan\CustomEventChannels.dll C:\ECMan\CustomEventChannels.cs



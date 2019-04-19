## Sysmon installation and configuration updates
## Glen Dosey doseyg@r-networks.net
## 2017-08-16
 
##This is where you set/update the configuration. It must be just the filename
$config = "sysmon-2018-0214.xml"
## Set this to your Windows Active Directory domain name
$domain = "domain"
 
##Sleep for 2 minutes to allow all networking to come up if used in startup script and not delayed by GPO
#Start-Sleep -s 120
 
##Hardcoded path variables, these shouldn't need to change after initial setup
$src_config = "\\$domain\NETLOGON\sysmon" + $config
$dst_config = "C:\Windows\" + $config
 
## Get the date for timestamping logfile
$date = Get-Date -Format g
 
## Determine processor architecture 32 or 64 bit
$arch = Invoke-Command -ScriptBlock { Get-WmiObject win32_processor -property AddressWidth | Select AddressWidth -ExpandProperty AddressWidth}
Add-Content "$env:temp\sysmon.txt" "$date Running Sysmon.ps1 update script for $config on $arch bit architecture"
 
if(Test-Path($dst_config)) {
                ##The configuration exists locally, so just check to see if sysmon is running
                $Sysmon64 = Get-Process "Sysmon64" -ErrorAction SilentlyContinue
                $Sysmon = Get-Process "Sysmon" -ErrorAction SilentlyContinue
                if($Sysmon64 or $Sysmon){
                                ##Sysmon is running, so nothing else to do
                }
                else{
                                ## Sysmon is not running, so re-install with current configuration to start service
                                Add-Content "$env:temp\sysmon.txt" "$date Sysmon does not appear to be running, reinstalling..."
                                Add-Content "$env:temp\sysmon.txt" "$date Copying $src_config"
                                Copy-Item $src_config $dst_config
                                if($arch -eq "64"){
                                                Invoke-Expression ("\\$domain\NETLOGON\sysmon\Sysmon64.exe -accepteula -i $dst_config")
                                                Add-Content "$env:temp\sysmon.txt" "$date Installed $arch bit Sysmon"
                                }
                                if($arch -eq "32"){
                                                Invoke-Expression ("\\$domain\NETLOGON\sysmon\Sysmon.exe -accepteula -i $dst_config")
                                                Add-Content "$env:temp\sysmon.txt" "$date Installed $arch bit Sysmon"
                                }
                }
}
else{
                ## Either the configuration is not up to date or Sysmon is not installed, so installing
                Add-Content "$env:temp\sysmon.txt" "$date Sysmon does not appear to be installed or is missing the current configuration, reinstalling..."
                Add-Content "$env:temp\sysmon.txt" "$date Copying $src_config"
                Copy-Item $src_config $dst_config
                if($arch -eq "64"){
                                Invoke-Expression ("\\$domain\NETLOGON\sysmon\Sysmon64.exe -accepteula -i $dst_config")
                                Add-Content "$env:temp\sysmon.txt" "$date Installed $arch bit Sysmon"
                }
                if($arch -eq "32"){
                                Invoke-Expression ("\\$domain\NETLOGON\sysmon\Sysmon.exe -accepteula -i $dst_config")
                                Add-Content "$env:temp\sysmon.txt" "$date Installed $arch bit Sysmon"
                }
}
---
layout: post
title:  "WSL fix to not use random subnets"
tags: [ Windows, WSL, ]
---

WSL is a nice way to work with Linux development environment from Windows. It works pretty decently after version 2, that switched to using proper virtualization instead of translating syscalls and other heavy magic.

Unfortunately, it has one serious problem: subnet for WSL is selected randomly from all possible private subnets, preeferably from `172.16.0.0/12` range. So you turn on your notebook, start WSL, then connect to work VPN and oops - that subnet is already used. Subnet is selected on first WSL start, restarting with `wsl --shutdown` does not help, only complete machine reboot does.



https://github.com/microsoft/WSL/issues/4467
https://github.com/microsoft/WSL/issues/4210


Static IP hack:
https://github.com/microsoft/WSL/issues/4210#issuecomment-648570493

Winkey+R - `taskschd.msc`


{% highlight powershell %}
# netsh interface show interface

# Start dummy interfaces protecting required gray subnets
netsh interface set interface "Vbox-WSL-fix-10" enable
netsh interface set interface "Vbox-WSL-fix-172-16" enable

# start WSL, that is forced to select subnet not overlapping with protected subnets
wsl ip a

# Stop dummy interfaces protecting required gray subnets
netsh interface set interface "Vbox-WSL-fix-10" disable
netsh interface set interface "Vbox-WSL-fix-172-16" disable
{% endhighlight %}

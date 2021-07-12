---
layout: post
title:  "WSL fix using random private subnets"
tags: [ Windows, WSL, ]
---

WSL is a nice way to work with Linux development environment from Windows. It works pretty decently after version 2, that switched to using proper virtualization instead of translating syscalls and other weird magic.

Unfortunately, it has one serious problem: subnet for WSL is selected randomly from all available private subnets, preferably from `172.16.0.0/12` range. So you turn on your notebook, start WSL, then connect to work VPN and oops - that subnet is already used 🤷‍♂️.

[Issue on Github](https://github.com/microsoft/WSL/issues/4467) to add subnet configuration support in WSL is open since 2019. People in comments contacted developers and their position is that this  by design, to make WSL networking transparent for newbies, and that won't be changed.

Funny thing, VirtualBox selects random private subnet for host-only networking adapters. But these subnets are fixed after initial creation and easily can be changed later. Newbies are happy, advanced users are happy, and nobody is having problems.

WSL selects random private subnet on first start, subnet will not be changed after `wsl --shutdown`, only reboot will help. But it does ignore subnets that are already in use. In comments to [the issue](https://github.com/microsoft/WSL/issues/4467) people proposed to create dummy network interfaces using all subnets except what we need WSL to start using. @jgregmac made this script: https://github.com/jgregmac/hyperv-fix-for-devs

For some reason it does not work for me, so I made my own version. It brings up dummy network interfaces, starts WSL and then brings them down.

First, I already have VirtualBox on my machine. So I will use it's host-only network interfaces to protect my subnets.

VritualBox: 

* File - Host NetworkManager

* Create - IPv4: `172.16.0.1` Network Mask: `255.240.0.0` DHCP Server: `[ ]`
* Create - IPv4: `10.0.0.1` Network Mask: `255.0.0.0` DHCP Server: `[ ]`

⚙Settings - Network & Internet - Change Adapter Options

* Rename interfaces to something more meaningful, like "Vbox-WSL-fix-10" and "Vbox-WSL-fix-172-16".

Create script `$env:USERPROFILE\bin\WSL-subnet-fix.ps1`:

{% highlight powershell %}
# Start dummy interfaces protecting required private subnets
netsh interface set interface "Vbox-WSL-fix-10" enable
netsh interface set interface "Vbox-WSL-fix-172-16" enable

# start WSL, that is forced to select subnet not overlapping with protected subnets
wsl ip a

# Stop dummy interfaces protecting required private subnets
netsh interface set interface "Vbox-WSL-fix-10" disable
netsh interface set interface "Vbox-WSL-fix-172-16" disable
{% endhighlight %}

Winkey+R - `taskschd.msc`

Create New Task

* General
    * Name: WSL-subnet-fix
    * (*) Run only when user is logged in
    * [x] Run with highest privileges
* Triggers
    * At log on: Specific user: your user
* Actions
    * Start a program
        * `powershell.exe`
        * Arguments: `-windowstyle hidden -file "C:\Users\<YOUR USERNAME>\bin\WSL-subnet-fix.ps1"`

Voila, you can use WSL and don't have it f up your work VPN.

If you need fixed static IP for your WSL machine, you may look at [this solution](https://github.com/microsoft/WSL/issues/4210#issuecomment-648570493) by @protang. It adds secondary fixed private subnet to WSL network interface.

---
layout: post
title:  "Persistent ipset for Ubuntu/Debian compatible with ufw and iptables-persistent"
tags: [iptables,ipset,ufw,iptables-persistent]
---

**UPD**: Added optional saving of changed ipset sets on service stop, thanks to [comment](https://www.reddit.com/r/linuxadmin/comments/92fkn5/persistent_ipset_for_ubuntudebian_compatible_with/e3agg55) by [Derhomp](https://www.reddit.com/user/Derhomp)

I could not find any standard solution for saving [ipset]((http://ipset.netfilter.org/)) rules together with iptables. Apparently, everybody who uses them have to create custom shell scripts for this task.

There are two most popular solutions for managing firewall in Ubuntu/Debian:
* [ufw](https://wiki.ubuntu.com/UncomplicatedFirewall) - I don't like it, but it is default.
* [iptables-persistent](https://packages.debian.org/stable/iptables-persistent) - if you are capable of writing firewall rules without crutches.

Using ipset with iptables has a subtelty: all sets should be defined before loading iptables rules that reffer to them.

Also, you can not destroy a set used by iptables rule, and you can not create a set with the same name as used one. So you can not just run `ipset restore -file myipset` if saved sets are already used by iptables.

Simpliest approach is to create all ipset sets once before loading any iptables rules.

Here is a systemd service to do that:

`/etc/systemd/system/ipset-persistent.service`:

```ini
[Unit]
Description=ipset persistent configuration
#
DefaultDependencies=no
Before=network.target

# ipset sets should be loaded before iptables
# Because creating iptables rules with names of non-existent sets is not possible
Before=netfilter-persistent.service
Before=ufw.service

ConditionFileNotEmpty=/etc/iptables/ipset

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/ipset restore -file /etc/iptables/ipset
# Uncomment to save changed sets on reboot
# ExecStop=/sbin/ipset save -file /etc/iptables/ipset
ExecStop=/bin/ipset flush
ExecStopPost=/bin/ipset destroy

[Install]
WantedBy=multi-user.target

RequiredBy=netfilter-persistent.service
RequiredBy=ufw.service
```

Now all that's left is to install it:

```bash
systemctl daemon-reload
systemctl enable ipset.service
```

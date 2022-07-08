---
layout: post
title:  "Limit frequency of new connection attempts with iptables module recent"
tags: [iptables, xt_recent]
redirect_from:
    - '/2018/07/07/block-ssh-bruteforce-with-iptables.html'
comments_by_utterance: true
---
Block for 20 seconds IP addresses that made more than 3 new connection attempts per 20 seconds:

```bash
cat > /etc/iptables/rules.v4 << EOF
*filter
:INPUT DROP [0:0]
:OUTPUT ACCEPT [0:0]
:ssh-ban - [0:0]
:ssh-check - [0:0]

-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ssh-check

-A ssh-check -m recent --name SSH --set --mask 255.255.255.255 --rsource
-A ssh-check -m recent --name SSH --rcheck --mask 255.255.255.255 --rsource --seconds 20 --hitcount 3 -j ssh-ban
-A ssh-check -j ACCEPT

-A ssh-ban -j LOG --log-prefix "anti-bruteforce ssh:" --log-level info
-A ssh-ban -j DROP
EOF

iptables-restore /etc/iptables/rules.v4
```

*Disclaimer:* Blocking brute-force attempts may not help much if weak passwords are used or if attackers use a large botnet. You should better use ssh keys, or if that is impossible use strong passwords. This is a simple solution, if you want something more advanced, you may use [fail2ban](https://www.fail2ban.org/).

Since client software usually makes more than one attempt to establish TCP connection, you may noitice that actual ban period is a couple times more than 20 seconds. And let's see how it works.

Chain `INPUT`:

1. Accept packets for already established connections without further filtering. It is required to not impede established ssh sessions.
1. Reject packets that are not starting a new connection or associated with known one. Not necessary, just adds a little more security.
1. For a packet initiating a new connection to tcp post 22: redirect to chain `ssh-check`

Chain `ssh-check`:

1. Add packet's source address with mask 255.255.255.255 to list named SSH; if it is already there - update existing entry
1. If the packet is already in the list and it was seen at least 3 times within 20 seconds:
  * Redirect it to the chain `block-ssh`
1. Accept the packet if it was not redirected by the previous rule

Chain `ssh-block`:
1. Log the blocked packet attempt to syslog with given message prefix and severity.
1. Drop the blocked packet

List of recently seen IP addresses with timestamps for several last packets is available in `/proc/net/xt_recent/SSH`. It can be manually altered:

```bash
# add addr
echo +addr >/proc/net/xt_recent/SSH
# remove addr
echo -addr >/proc/net/xt_recent/SSH
# flush list - remove all entries
echo / >/proc/net/xt_recent/SSH
```

Number of addresses and packets for address remembered per table and other settings may be changed as parameters of kernel module `xt_recent`:

```bash
modinfo xt_recent | grep ^parm
parm: ip_list_tot:number of IPs to remember per list (uint)
parm: ip_list_hash_size:size of hash table used to look up IPs (uint)
parm: ip_list_perms:permissions on /proc/net/xt_recent/* files (uint)
parm: ip_list_uid:default owner of /proc/net/xt_recent/* files (uint)
parm: ip_list_gid:default owning group of /proc/net/xt_recent/* files (uint)
parm: ip_pkt_list_tot:number of packets per IP address to remember (max. 255) (uint)
```

See also:

* [man iptables-extensions](http://manpages.ubuntu.com/manpages/bionic/man8/iptables.8.html)

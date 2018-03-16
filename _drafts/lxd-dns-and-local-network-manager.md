---
layout: post
title:  "Resolve LXD container names on host system with network-manager"
tags: [lxd,dns,dnsmasq,network-manager]
---
LXD containers inside a bridge can resolve each other's name. Host machine does not see this names, let's fix it.

I've found the answer in [this forum post](https://discuss.linuxcontainers.org/t/dns-for-lxc-containers/235/4) by [simos](https://blog.simos.info/).

LXD configuration:

`lxc network show lxdbr0`

```yaml
config:
  dns.domain: lxd
  dns.mode: dynamic
  ipv4.address: 10.10.10.1/24
  ipv4.dhcp.ranges: 10.10.10.2-10.10.10.254
  ipv4.nat: "true"
  ipv6.address: none
description: ""
name: lxdbr0
type: bridge
used_by:
managed: true
```

LXD launches dnsmasq instance, that provides DHCP and DNS for containers inside a bidge.

Desktop Ubuntu uses NetworkManager. It also launches dnsmasq instance. Additional settings for it can be configured by files in `/etc/NetworkManager/dnsmasq.d/` directory(it is passed with `--conf-dir` parameter).

`/etc/NetworkManager/dnsmasq.d/lxd.conf`:

```ini
# Use specified server for lxd domain
server=/lxd/10.10.10.1
# Use specified server for DNS reverse lookup
server=/10.10.10.in-addr.arpa/10.10.10.1
# Do not bind to wildcard address, but bind to avaiable interfaces
bind-interfaces
# Except this one
except-interface=lxdbr0
```

Now we should kill dnsmasq instance, NetworkManager will launch a new one automatically:

`sudo pkill -U nobody dnsmasq`

Filter by user is used to avoid killing dnsmasq used by LXD.

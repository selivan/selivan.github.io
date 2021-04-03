---
layout: post
title:  "Instantly syncronize time with NTP on host startup"
tags: [ntp, chrony]
---

Virtual machines, for example AWS instances, sometimes start with clock runnung several minutes behind. NTP solves this issue, but ntp daemon tries to syncronize clock gradually, to prevent bugs in software. Therefore sometimes AWS instance spend some time after start working with clock running significantly behind. This behaviour is not always desired.

Here is a workaround to syncronize time at startup, using [chrony](https://chrony.tuxfamily.org/) NTP client.

`/etc/systemd/system/chrony-ntp-sync-once.service`:

```
[Unit]
Description=Quick sync NTP one time and exit

# FIXME
Wants=network-online.target
After=network-online.target

Before=nginx.service mysql.service

[Service]
Type=oneshot
RemainAfterExit=True
ExecStartPre=sh -c "while ! ip r | grep ^default; do sleep 0.5; echo waiting for default route to appear; done"
ExecStart=/usr/sbin/chronyd -q -t 30

[Install]
WantedBy=multi-user.target
```

Simple `After=network-online.target` doesn't seem to work, so I use a [workaround](/2020/12/23/systemd-broken-network-online-target-workaround.html).

FIXME:

Wants=network-online.target leads to 

```
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: Stopped Quick sync NTP one time and exit.
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found ordering cycle on network-online.target/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found dependency on network.target/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found dependency on chrony-ntp-sync-once.service/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Job network-online.target/start deleted to break ordering cycle startin>
```

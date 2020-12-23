---
layout: post
title:  "Syncronize time by NTP before starting any services in Linux"
tags: [ ntp, chrony, systemd ]
---

Servers often have wrong clock on startup. NTP services, like `ntp`, `chrony` and `systemd-timesyncd` try to correct clock gradually to avoid weird bugs in software. Therefore, if server has a large clock offset on startup, it works with incorrect clock for several minutes.

In my experience, AWS instances may have clock error up to 5 minutes on startup. Server writing log timestamps 5 minutes in the past or in the future is not always a good idea.

Solution is to force NTP time syncronization once before starting any other services. I prefer to use `chrony`: it can act both as always runnig NTP client and one-time syncronization tool; `chronyc` clearly reports syncronization status, making it easy to monitor.

`/etc/systemd/system/ntp-sync-once.service` :

```ini
[Unit]
Description=Quick sync NTP one time and exit

Wants=network-online.target
After=network-online.target
# You may add explicit ordering for your important services
Before=nginx.service mysql.service

[Service]
Type=oneshot
RemainAfterExit=True
# Ugly workaround for not working properly network-online.target
ExecStart=sh -c "while ! ip r | grep ^default; do sleep 0.5; done"
# -t <timeout in seconds>  timeout after which chronyd will exit even if clock is not syncronized
ExecStart=/usr/sbin/chronyd -q -t 30

[Install]
WantedBy=multi-user.target
```

`network-online.target` sometimes is [not working as expected](/2020/12/23/systemd-broken-network-online-target-workaround.html), first `ExecStart` line is a workaround for that.

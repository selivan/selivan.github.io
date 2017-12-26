---
layout: post
title:  "Console autologin for Ubuntu with systemd(15.04 and higher)"
tags: [autologin,console,getty,ubuntu,systemd]
---

/etc/systemd/system/getty@tty1.service.d/override.conf

systemctl edit getty@tty1

```ini
[Service]
ExecStart=
ExecStart=-/sbin/mingetty --autologin ubuntu --noclear %I
```

First `ExecStart` entry is required, if you want to re-define value defined in global unit file `/lib/systemd/system/getty@.service`.

---
layout: post
title:  "Systemd service that is always restarted on failure"
tags: [autologin,console,getty,ubuntu,systemd]
---
Use `systemctl edit foobar.service` or manually edit `/etc/systemd/system/foobar.service.d/override.conf` and run `systemctl deamon-reload`.

```ini
[Service]
Restart=always
RestartSec=2

[Unit]
StartLimitInterval=0
```


---
layout: post
title:  "Console autologin for Ubuntu with systemd(15.04 and higher)"
tags: [autologin,console,ubuntu,systemd]
comments_by_utterance: true
---
`agetty` version from `util-linux` starting from Ubuntu 16.04 has option `--autologin`, but for some reason it doesn't work for me: creates empty non-responsive terminal. So let's use `mingetty` instead.

`apt install mingetty`

Use `systemctl edit getty@tty1` or manually edit `/etc/systemd/system/getty@tty1.service.d/override.conf` and run `systemctl daemon-reload`.

```ini
[Service]
ExecStart=
ExecStart=-/sbin/mingetty --autologin ubuntu --noclear %I
```

First `ExecStart` empty assignment is required, if you want to re-define value in global unit file `/lib/systemd/system/*.service`.

`-` prefix makes systemd ignore non-zero exit code and consider it success.

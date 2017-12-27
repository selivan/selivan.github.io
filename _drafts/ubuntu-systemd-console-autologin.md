---
layout: post
title:  "Console autologin for Ubuntu with systemd(15.04 and higher)"
tags: [autologin,console,getty,ubuntu,systemd]
---
`agetty` version from `util-linux` in Ubuntu Xenial has option `--autologin`, but for some reason it ddoesn't work for me: creates empty non-responsive terminal. So let's use `mingetty` instead. Btw, it had autologin option for a long time, while `agetty` didn't.

`apt install mingetty`

Use `systemctl edit getty@tty1` or manually edit `/etc/systemd/system/getty@tty1.service.d/override.conf` and run `systemctl deamon-reload`.

```ini
[Service]
ExecStart=
ExecStart=-/sbin/mingetty --autologin ubuntu --noclear %I
```

First `ExecStart` empty assignment is required, if you want to re-define value in global unit file `/lib/systemd/system/*.service`.

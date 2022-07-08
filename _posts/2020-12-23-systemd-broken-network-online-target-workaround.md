---
layout: post
title:  "Systemd broken network.online target workaround"
tags: [ systemd ]
comments_by_utterance: true
---

[man systemd.special](https://www.freedesktop.org/software/systemd/man/systemd.special.html) says: 

> Units that strictly require a configured network connection should pull in network-online.target (via a Wants= type dependency) and order themselves after it.

Despite that, I ran into a problem: service that requires outside network to be immediately available fails to start with configuration like described in manual:

```ini
[Unit]
Wants=network-online.target
After=network-online.target
```

Here is an ugly workaround for that:

```ini
[Unit]
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=sh -c "while ! ip -4 r | grep ^default; do echo waiting for ipv4 default route to appear; sleep 0.5; done"
ExecStart=<actual service here>
```

If you want not just default route available, but certain IP address:

```ini
ExecStart=sh -c "while ! ping -c 1 -W 0.5 <IP>; do true; done"
```

---
layout: default
title:  "Self-hosted socks5 or shadowsocks server in a single command"
---
Create self-hosted [socks5](https://en.wikipedia.org/wiki/SOCKS) or [shadowsocks](https://shadowsocks.org/) server in a single command.

Feel free to send any issues or improvements to [github project](https://github.com/selivan/selivan.github.io-socks/issues).

# socks5
`curl {{ site.url }}/socks.txt | sudo bash`

If you would like to manually set port and/or password:

```bash
export PORT=8080; export PASSWORD=mypass
curl {{ site.url }}/socks.txt | sudo --preserve-env bash
```

This creates self-hosted [SOCKS5](https://en.wikipedia.org/wiki/SOCKS) server powered by [Dante](http://www.inet.no/dante/). Supported Linux distributions:

* Ubuntu 16.04 Xenial
* Ubuntu 18.04 Bionic
* Ubuntu 20.04 Focal
* CentOS 7 and Oracle Linux 7.5 (thanks to [Vlad Safronov](https://github.com/vladsf))

# shadowsocks

`curl {{ site.url }}/shadowsocks.txt | sudo bash`

If you would like to manually set port and/or password:

```bash
export PORT=8080; export PASSWORD=mypass
curl {{ site.url }}/shadowsocks.txt | sudo --preserve-env bash
```

This creates self-hosted [shadowsocks](https://shadowsocks.org/) server. Clients:
* Android: [shadowsocks by Max Lv](https://play.google.com/store/apps/details?id=com.github.shadowsocks)
* Other devices: [shadowsocks clients](https://shadowsocks.org/en/download/clients.html)

Supported Linux distributions:

* Ubuntu 16.04 Xenial
* Ubuntu 18.04 Bionic
* CentOS 7 and RHEL 7 (thanks to Octavian Dodita octavian2204[anti-spam-dog]gmail.com )

# P.S.

This is just a basic proxy, very simple to install and use. If you are interested in a more functional and complex soltion, you may check out [Streisand Effect](https://github.com/StreisandEffect/streisand).

---
layout: default
title:  "Self-hosted socks5 or shadowsocks server in a single command"
---
Create self-hosted socks5 or shadowsocks server in a single command.

This is just a basic proxy, very simple to install and use. If you are interested in a more functional and complex soltion, you may check out [Streisand Effect](https://github.com/StreisandEffect/streisand).

Feel free to send any issues or improvements [here](https://github.com/selivan/selivan.github.io-socks/issues).

## socks5
`curl {{ site.url }}/socks.txt | sudo bash`

If you would like to manually set port and/or password:

```bash
export PORT=8080; export PASSWORD=mypass
curl {{ site.url }}/socks.txt | sudo --preserve-env bash
```

This creates self-hosted [SOCKS5](https://en.wikipedia.org/wiki/SOCKS) server powered by [Dante](http://www.inet.no/dante/). Supported Linux distributions:

* Ubuntu 16.04 Xenial
* Ubuntu 18.04 Bionic

## shadowsocks

`curl {{ site.url }}/shadowsocks.txt | sudo bash`

If you would like to manually set port and/or password:

```bash
export PORT=8080; export PASSWORD=mypass
curl {{ site.url }}/shadowsocks.txt | sudo --preserve-env bash
```

This creates self-hosted [shadowsocks](https://shadowsocks.org/en/index.html) server. Supported Linux distributions:

* Ubuntu 16.04 Xenial
* Ubuntu 18.04 Bionic

---
layout: default
title:  "Self-hosted socks5 server in a single command"
---
`curl {{ site.url }}/socks.txt | sudo bash`

If you would like to manually set port and/or password:

```bash
export PORT=8080; export PASSWORD=mypass
curl {{ site.url }}/socks.txt | sudo bash
```

This creates self-hosted [SOCKS5](https://en.wikipedia.org/wiki/SOCKS) server powered by [Dante](http://www.inet.no/dante/). Supported Linux distributions:
* Ubuntu 16.04 Xenial

Feel free to send any issues or improvements [here](https://github.com/selivan/selivan.github.io-socks/issues).

This is just a basic proxy, very simple to install and use. If you are interested in a more functional and complex soltion, you may check out [Streisand Effect](https://github.com/StreisandEffect/streisand).

---
layout: default
title:  "Self-hosted socks5 server in single command"
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

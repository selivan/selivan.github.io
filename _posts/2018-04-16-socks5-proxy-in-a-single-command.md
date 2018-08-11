---
layout: post
title:  "Setup a SOCKS5 proxy in a single command"
tags: [socks,proxy]
comments_by_disqus: true
---
Due to recent block of Telegram by Russian Censorship, I created a script to get your own [SOCKS5](https://en.wikipedia.org/wiki/SOCKS) proxy in a single command: [{{ site.url }}/socks](/socks)

VPN is a also a good solution, but on mobile devices it consumes additional power. And since all traffic to Telegram servers is encrypted anyway, you may as well use SOCKS proxy which does not eat your battery.

Of course, it is a bad practive to pipe into `sudo bash` something that you have found on the Internet. But if you use some expendable vm/container that serves only one purpose, it's fine.

If you are looking for a more complex and functional solution to bypass censorship, you may check out [Streisand Effect](https://github.com/StreisandEffect/streisand).

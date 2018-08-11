---
layout: post
title:  "Mikrotik and OpenVPN 2.3 compatibility: error 'Bad LZO decompression header byte: 69'"
tags: [mikrotik,routeros,openvpn]
comments_by_disqus: true
---

Mikrotik RoutesOS has limited [OpenVPN support](https://wiki.mikrotik.com/wiki/OpenVPN#Supported): only TCP connections, no UDP, and no [LZO](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Oberhumer) compression.

I had to configure Linux OpenVPN(ver. 2.3) server and Mikrotik client. Seems easy. Connection was establishing normally, client got authentificated, and then error `Bad LZO decompression header byte: 69` arised. Packets were not transmitted over the connection and finally it was killed on `ping-restart` timeout.

I tried not mentioning `comp-lzo` at all, setting it to `no`, to `auto` and pushing it to the client: `push "comp-lzo no"`. But the error was still there.

Finally I figured out, that there is one more LZO-related option, `comp-noadapt`, and it does the trick. I got stable working connection.

This option is supposed to make compression adaptive, allowing not to compress already compressed data, like transfer of large compressed file. I suppose, this adaptive algorithm somehow breaks `comp-lzo no` option, at least for several first packets.

Hope this article will save you some time, that I had to lose on debugging this annoying error.

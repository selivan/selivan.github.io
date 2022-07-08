---
layout: post
title:  "Perona XtraDB Cluster 5.5 work over IPv6"
tags: [mysql,pxc]
comments_by_utterance: true
---

PXC 5.5 does not work with IPv6 out-of-the-box: SST is broken and it can not parse IPv6 addresses from config.

To avoid error with parsing IPv6 addresses, use hostnames instead.

To make SST work, use [sockopt](https://www.percona.com/doc/percona-xtradb-cluster/5.5/manual/xtrabackup_sst.html#sockopt) to force `socat` use IPv6. Warning: this will break SST for IPv4-only hosts.

Here is example config:

```ini
[mysqld]
wsrep_provider_options = "gmcast.listen_addr=tcp://[::]:4567; ist.recv_addr=HOST-IP6-NAME:4568"
wsrep_sst_receive_address = HOST-IP6-NAME:4444
wsrep_cluster_address = gcomm://HOST-IP6-NAME:4567,PEER2-IP6-NAME:4567,PEER3-IP6-NAME:4567

[sst]
sockopt = ',pf=ipv6'
```

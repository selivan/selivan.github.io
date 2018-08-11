---
layout: post
title:  "Redis replication: prevent split-brain (additional master) in case of network partition"
tags: [redis]
comments_by_disqus: true
---
Redis replication group can go multi-master on network partition, if old master restarts automatically. Sentinels will eventually fix it to become slave of new one, but that takes some time. If some application continues writing to old master, some data will be lost. To prevent this issue, write this line in every `redis.conf`:

```
slaveof 0.0.0.0 6739
```

And make `redis.conf` permissions strict, so that redis would not be able to rewrite it with [CONFIG REWRITE](http://redis.io/commands/config-rewrite). Every host after restart will become slave with broken master connection, multi-master will never happen. If all hosts were just booted and there is no master, you should choose one by giving it command `slaveof no one`. After some timeout sentinels will fix restarted host to replicate from new master.

And now, since you will never have second stand-alone master, you can use it with haproxy on each node to relieve clients from dealing with sentinels for every connection. I have found original idea in this post: [haproxy blog - advanced redis health check](http://blog.haproxy.com/2014/01/02/haproxy-advanced-redis-health-check/)

`haproxy.cfg`:

```config
defaults REDIS
    mode tcp
    timeout connect  4s
    timeout server  30s
    timeout client  30s

frontend ft_redis
    bind 127.0.0.1:6380 name redis
    default_backend bk_redis

backend bk_redis
    option tcp-check
    tcp-check send PING\r\n
    tcp-check expect string +PONG
    tcp-check send info\ replication\r\n
    tcp-check expect string role:master
    tcp-check send QUIT\r\n
    tcp-check expect string +OK
    server R1 192.168.0.1:6379 check inter 1s
    server R2 192.168.0.2:6379 check inter 1s
    server R3 192.168.0.3:6379 check inter 1s
```

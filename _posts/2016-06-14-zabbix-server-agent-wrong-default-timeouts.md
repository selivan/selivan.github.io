---
layout: post
title:  "Zabbix: unawailable items and hosts caused by wrong default timeout settings"
tags: zabbix
comments_by_utterance: true
---

I am using zabbix for a long time, it is good monitoring system, simple enough and powerful. Recently I found a subtle problem with it's default settings, which occures very occasionally and leads to temporal stale items data or quick whole host unavailability, monitored by triggers like `agent.ping.nodata()`.

I created a ticket [ZBX-10868](https://support.zabbix.com/browse/ZBX-10868), but zabbix guys think that this is not problem, but misconfiguration. Ticket is closed as "won't fix". They changed default `Timeout` value for server and proxy in [ZBXNEXT-2637](https://support.zabbix.com/browse/ZBXNEXT-2637), so this is not a big problem now. But there is still a lot of old installations and old default values in configs.

Root of the problem: by default, both agent and server had `Timeout = 3`. For agent, it defines maximum time to wait for item checks. For server, it defines how long to wait for agent, SNMP device or external check. And here comes the best part: one timeouting item sometimes blocks other items from transferring to server. After fix in [ZBX-4284](https://support.zabbix.com/browse/ZBX-4284), Zabbix tries different items for checking host unreachable pollers. But if you have a lot of broken timeouting items on agent, it anyway takes a long time. Triggers like `agent.ping.nodata()` may be fired from time to time, and other good non-timeouting items may be lost.

So, if you want to aviod _rarely appearing mysterios problems_ with zabbix, you should always keep `Timeout` on server and proxy larger than on agent.

For example, check `net.tcp.port[IP,port]` has no timeout parameter, and if IP is not answering, you have broken timeouting item. If IP was available when you applied template with new items, you won't notice anything wrong. To make tcp check with defined timeout, you can use this UserParameter for *nix hosts:

```config
# tcp_connect_check[IP, port, timeout_seconds]
# Security: UnsafeUserParameters=no disables sending some symbols to custom check, never change it
UserParameter=tcp_connect_check[*], /bin/nc -z "$1" "$2" -w "$3"; echo $?
```

Or you can upvore feature request to add timeout parameter to `net.tcp.port`: [ZBXNEXT-3295](https://support.zabbix.com/browse/ZBXNEXT-3295).

Also long running UserParameters can cause timeouting items.

Useful link: zabbix documentation on unreachable/unavailable behaviour: [items-unreachability](https://www.zabbix.com/documentation/3.0/manual/appendix/items/unreachability).

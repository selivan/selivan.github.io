---
layout: post
title:  "Zabbix: aggregate check for text items workaround"
tags: [zabbix]
comments_by_utterance: true
---

In Zabbix you can check things like total disk space or average CPU load for a whole host group using [aggregate checks](https://www.zabbix.com/documentation/4.0/manual/config/items/itemtypes/aggregate). Available aggregate functions are `grpavg`, `grpmax`, `grpmin`, `grpsum`.

If you have an item returning text information(item types "Character" or "Text"), you can not use this functions to check something for a whole group of hosts. In some cases you can use a workaround for that.

Let's say, all hosts in group have an item `redis.info[replication,role]`, returning redis replication role: "master" or "slave". You would like to check that only one server in group have the master role.

Create on each host a [calculated item](https://www.zabbix.com/documentation/4.0/manual/config/items/itemtypes/calculated) `redis.is_master` with formula `str("redis.info[replication,role]",master)`.

Trigger function `str` returns 1 if `redis.info[replication,role]` is `master` and 0 otherwise.

Now you can create an aggregate item with key `grpsum["web","redis.is_master",last,0]`. In trigger you may check if the aggregare item equals 1 - that means, you have exactly one master server.

This way you may check count of items that are equal to some pre-defined string in a whole host group.

I recommend to group aggregate checks into separate template and to assign that template to zabbix server(s) host(s). This way you won't lose your check if some server in host group goes away, and you would not get excessive notifications if all servers in host group light up the trigger.

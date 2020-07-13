---
layout: post
title:  "Integration elastalert with Zabbix"
tags: [elastalert,elasticsearch, zabbix]
---

[Elastalert](https://elastalert.readthedocs.io/) is a popular framework for alerting on events in Elasticsearch data. It can be integrated with a lot of notification systems - email, slack, telegram, PagerDuty and a lto of others, including sending alerts to Zabbix: [zabbix alerter type](https://elastalert.readthedocs.io/en/latest/ruletypes.html#zabbix). It is convenient if you already has your monitoring notifcations system configured in Zabbix: which type of problems send alert to which groups of people, via different media depending on severity, with escalations if necessary and so on.

Zabbix integration has 2 problems, though. First, it allows only sending 0 and 1 to zabbix [trapper items](https://www.zabbix.com/documentation/current/manual/config/items/itemtypes/trapper), no text data. Second, it doesn't work: [issue #2586](https://github.com/Yelp/elastalert/issues/2586). Probably it got broken in recent elastalert versions.

Luckily elastalert supports `command` alert type for custom commands, which is enough to have zabbix support and also to make alerts with text data, not just 1 and 0.

Let's write alerts to log files and read them using zabbix agent [log monitoring](https://www.zabbix.com/documentation/current/manual/config/items/itemtypes/log_items) capability. That allows to send text if necessary and also is more reliable than a trapper item, which may lose a value if sender and server connectivity is shortly interrupted.

Creating a zabbix item and a trigger each time you need a new alert looks like a lot of unnecessary monotonous work, and a lot of chanses to make a mistake in that work. If you use SCM like Puppet/Chef/Ansible/etc it's easier to generate items and triggers from your elastalert rules with Zabbix [LLD](https://www.zabbix.com/documentation/current/manual/discovery/low_level_discovery)(Low Level Discovery).

Zabbix does not support getting trigger severity from LLD data, so you need a separate item for each severity. Also, you can not use exactly the same item name from one discovery rule in another discovery rule, so they all should be named different. 5 levels of severity(information/warning/average/high/disaster), 2 types of triggers - 0/1 and text, that gives us 10 discovery rules.


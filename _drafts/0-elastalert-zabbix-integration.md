---
layout: post
title:  "Integration elastalert with Zabbix"
tags: [elastalert,elasticsearch, zabbix]
---

[Elastalert](https://elastalert.readthedocs.io/) is a popular framework for alerting on events in Elasticsearch data. It can be integrated with a lot of notification systems - email, slack, telegram, PagerDuty and a lto of others, including sending alerts to Zabbix: [zabbix alerter type](https://elastalert.readthedocs.io/en/latest/ruletypes.html#zabbix).

Zabbix integration has 2 problems, though. First, it allows only sending 0 and 1 to zabbix [trapper items](https://www.zabbix.com/documentation/current/manual/config/items/itemtypes/trapper), no text data. Second, it doesn't work: [issue #2586](https://github.com/Yelp/elastalert/issues/2586). Probably it got broken in recent versions.

But elastalert supports `command` alert type, allowing custom commands, which is enough to have zabbix support and also to make alerts with text data, not just 1 and 0.

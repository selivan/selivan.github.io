---
layout: post
title:  "Zabbix: user parameters items become unavailable if non-zero code is returned by command, triggers break, no alerts produced."
tags: zabbix
---

Example:

```
UserParameter=pxc_status_db01, ( curl --max-time 4 --silent --head "http://db01:9200/" || echo 'HTTP/1.0 0' ) | grep '^HTTP/...' | cut -d' ' -f2
```

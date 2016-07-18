---
layout: post
title:  "Zabbix: user parameter non-zero exit code silently breaks triggers"
tags: zabbix
---

If zabbix userparameter command rerurns non-zero exit code, item becomes "unawailable". 

```
UserParameter=pxc_status_db01, ( curl --max-time 4 --silent --head "http://db01:9200/" || echo 'HTTP/1.0 0' ) | grep '^HTTP/...' | cut -d' ' -f2
```

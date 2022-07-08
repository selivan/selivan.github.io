---
layout: post
title:  "Zabbix: user parameter command non-zero exit code silently breaks triggers"
tags: zabbix
reddit: https://www.reddit.com/r/zabbix/comments/4tgnd8/user_parameter_command_nonzero_exit_code_silently/
comments_by_utterance: true
---

If zabbix userparameter command returns non-zero exit code, item becomes "unsupported". Triggers depending on this item become broken **without any alert**. Here is a good example: you monitor number of active php_fpm processes by getting and parsing URL specified in [pm.status_path](http://php.net/manual/en/install.fpm.configuration.php) . But when number of active processes reaches maximum, it won't work: to display status, you need new php process, and it can not start any more.

First solution: you can enable monitoring of not supported items in Configuration - Actions - "Event source:internal" - "Report not supported items". It is not always a good option, because you may have many periodically unsupported items in your setup, and you don't want to be bothered by every one of them.

Here is second solution: write user parameter commands so, that if command result was non-zero, they report unusual value, switching trigger to 'ERROR':

```config
UserParameter=php_fpm.active_processes, ( curl --max-time 2 --silent http://localhost/php_fpm_status || echo 'active processes: 9999' ) | grep '^active processes' | tr -s ' ' | cut -d' ' -f 3
```

**UPDATE**: Since 3.4 Zabbix checks user parameters exit code and shows stdout and stderr in frontend: [documentation](https://www.zabbix.com/documentation/3.4/manual/appendix/command_execution#exit_code_checking). But relevant trigger becomes silently broken anyway.

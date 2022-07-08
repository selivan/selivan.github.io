---
layout: post
title:  "Running syslog-ng as unprivileged user"
tags: [syslog,syslog-ng]
comments_by_utterance: true
---
By default, at least in Debian/Ubuntu, syslog-ng is launched with root privileges. This is not good. Let's try to run it from `syslog` user, like rsyslog.

Give it required permissions on `/var/lib/syslog-ng`:

```bash
chown syslog /var/lib/syslog-ng
```

Modify service config script `/etc/default/syslog-ng`:

```bash
SYSLOGNG_OPTS="-u syslog -g syslog"

if [ ! -e /var/run/syslog-ng.pid ] then
	touch /var/run/syslog-ng.pid
fi
chown syslog /var/run/syslog-ng.pid
chmod 0664 /var/run/syslog-ng.pid

```

We added required user and group to daemon options and created pid file for it: it creates pid before dropping privileges, so later it can't use it. At least I saw this behaviour in syslog-ng 3.5 from Ubuntu 14.04.Trusty. Restart syslog-ng service.

Voila! Now it is running from unprivileged user `syslog`.

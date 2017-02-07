---
layout: post
title:  "Rsyslog configuration: forwarding log files, saving file names, handle multi-line messages and failover"
tags: [rsyslog, syslog]
---

## Task

Forward logs to log server. If it's unavailable, do not loose messages, but preserve and and send later. Handle multi-line messages correctly.

Additional goals:
* server reconfiguration is not required for new log files, client reconfiguration is sufficiet
* forwarding of all log files with name matching wildcard, saved separately on server with same names

Only Linux servers are used.

## Choise of software

Why use syslog in our days? We have elastic beats, logstash, systemd-journal-remote and a lto mode new shiny technologies?


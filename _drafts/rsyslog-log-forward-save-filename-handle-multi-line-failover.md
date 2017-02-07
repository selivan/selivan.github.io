---
layout: post
title:  "Rsyslog configuration: forwarding log files, saving file names, handle multi-line messages and failover"
tags: [rsyslog, syslog]
---

*This is translation of my original article in russian: https://habrahabr.ru/post/NNNNN*

## Task

Forward logs to log server. If it's unavailable, do not loose messages, but preserve and and send later. Handle multi-line messages correctly.

Additional goals:
* server reconfiguration is not required for new log files, client reconfiguration is sufficiet
* forwarding of all log files with name matching wildcard, saved separately on server with same names

Only Linux servers are used.

## Choise of software

Why use syslog in our days? We have elastic beats, logstash, systemd-journal-remote and a lto mode new shiny technologies?

* It is standard for logging in POSIX-like systems  
Some software, like haproxy, uses only syslog. So you can not completely eliminate it
* It is used by network hardware
* It has more complex setup, but a log more features, then competitor solutions  
For example, Elastic Filebeat still con not use inofity.
* Low memory usage. Can be used in embedded systems after [some tuning](http://wiki.rsyslog.com/index.php/Reducing_memory_usage).
* Allows to change message before saving and forwarding.  
Unusual requrement, but sometimes it's necessary. For example, [PCI DSS](https://en.wikipedia.org/wiki/PCI_DSS) in section 3.4 requires to mask or cypher card numbers, in case they are saved on disk. The nuance is: if somebody entered card number in search or contacts form, and you saved the query, you have broke the requirement.

*Observation*: users are entering card number into every input field on a page, and sometimes try to tell it support together with CVV and PIN.

## Message format and legacy

*TLDR*: everything is broken

Syslog appeared in 80-x, and quickly became logging standard for Unix-like OS and network hardware.


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

Syslog appeared in 80-x, and quickly became logging standard for Unix-like OS and network hardware. There were no stanrard, everybody was writing code just to be compatible with existing software. In 2001 IETF described current situation in RFC 3164(status "informational"). Implementations vary a lot, so it states "The payload of any IP packet that has a UDP destination port of 514 MUST be treated as a syslog message". Later IETF tried to create standard format in RFC 3165, but this document was unconvenient, at this moment there is no any alive software implementation. In 2009 RFC 5424 was approved, defining structured messages, but it is rarely used.

[Here](http://www.rsyslog.com/doc/syslog_parsing.html) you can read what rsyslog author Rainer Gerhards does think about syslog standard situation. In fact, everybody is implementing syslog as he likes, and syslog server has the task to interpret anything it recieves. For example, rsyslog has [special module](http://www.rsyslog.com/doc/v8-stable/configuration/modules/pmciscoios.html) to parse format used by CISCO IOS. For the worst cases since rsyslog 5th version you can define custom parsers.

Transferred over network syslog message looks something like this:

```
<PRI> TIMESTAMP HOST TAG MSG
```

* `PRI` - priority. Calculated as `facility * 8 + severity`.
  * Facility has values from 0 to 23 for different system services: 0 - kernel, 2 - mail, 7 - news. Last 8 - from local0 to local7 - are used for services outside this pre-defined categories. [Complete list](https://en.wikipedia.org/wiki/Syslog#Facility).
  * Severity has values from 0(emergency, most important) to 7(debug, least important). [Complete list](https://en.wikipedia.org/wiki/Syslog#Severity_level).
* `TIMESTAMP` - time,  usually in format like `Feb  6 18:45:01`. According to RFC 3194, it also can have time format of ISO 8601: `2017-02-06T18:45:01.519832+03:00` with better precision and timezone.
* `HOST` - name of host, which generated the message
* `TAG` - contains name of program that generated the message. Not more then 32 alphanumeric characters, though in fact many implementations allow more. Any non-alphanumeric symbol stops `TAG` and starts `MSG`, colon is used usually. Sometimes can have process id in square brackets. `[ ]` are not alphanumeric, so it should be part of a message. But usually implementations consider it part of `TAG` field, and consider `MSG` start after ": " symbols
* `MSG` - message. Because of uncertainty about where `TAG` ends and it starts, often gets additional space symbol at the beginning. Can not contain new line symbols: by standard, they are frame delimeters, effectively starting new syslog message. Methods to actually transfer multi-line message:
  * escaping. On recieving side we have message with `#012` instead of new lines
  * using octed-based TCP Framing, described in RFC 5425 for TLS-enabled syslog. Non-standard, only few implementations can do it

### Alternative: RELP

If messages are transferred between hosts using rsyslog, instead of plain TCP you can use [RELP](http://www.rsyslog.com/doc/relp.html) - Reliable Event Logging Protocol. It was created for rsyslog, now it's supported by some other systems.

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

If messages are transferred between hosts using rsyslog, instead of plain TCP you can use [RELP](http://www.rsyslog.com/doc/relp.html) - Reliable Event Logging Protocol. It was created for rsyslog, now it's supported by some other systems. For instance, it's supported by Logstash and Graylog. Uses TCP for transport. Can optionally encrypt messages with TLS. It's more reliable than plain TCP syslog, because it does not loose messages when connection breaks. It solves problem with multi-line messages.

## rsyslog configuration

In contrast to the second popular syslog deamon, syslog-ng, rsyslog is compatible with configs of old syslogd:

```bash
auth,authpriv.*            /var/log/auth.log
*.*;auth,authpriv.none     /var/log/syslog
*.*       @syslog.example.net
```

Because rsyslog has a lot more features than it's predecessor, config format was extended with additional directives, starting from `$` sign:

```
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$WorkDirectory /var/spool/rsyslog
$IncludeConfig /etc/rsyslog.d/*.conf
``` 

Starting with 6th version c-like RainerScript format was introduced. It allows to specify complex rules for message processing.

Because new config formats were created gradually and compatible with old format, then there is couple of flaws:
* some plugins(but I haven't seen such ones) can lack new format support, and still require old configuration directives
* configuring with old directives does not always work as expexted for new format:
  * if module `omfile` is called with old format: `auth,authpriv.*  /var/log/auth.log`, then owner and group of created files are defined by old directives `$FileOwner`, `$FileGroup`, `$FileCreateMode`. And if it is called with `action(type="omfile" ...)`, then tihs directives are ignored and you should configure it in module loading statement or inside action itself.
  * Directives like `$ActionQueueXXX` are configuring queue used by next Action, and after their values are reset.
* semicolon is forbidden somewhere, and strictly required in other places(second happes less often).

To avoid stumbling on this flaws, one should follow this simple rules:
* for small and simple configs use old well-known format: `:programname, startswith, "haproxy"  /var/log/haproxy.log`
* for complex message processing and for fine tuning of action parameters always use RainerScript, without legacy directives like `$DoSomething`.

Read more about config format [here](http://www.rsyslog.com/doc/v8-stable/configuration/basic_structure.html#configuration-file).

## Message processing

* All messages comes from one of Inputs and fall into assigned RuleSet. If it is not set explicitly, default RuleSet will be used. All message processing directives ouside separate RuleSet blocks are part of default RuleSet. For instance, all directives from traditional format:  
`local7.*  /var/log/myapp/my.log`
* Input has assigned list of message parsers. If not set explicitly, default set of parsers for traditional syslog format will be used
* Parset extracts properties from message. Some of most used:
  * `$msg` - message
  * `$rawmsg` - whole message before parsing
  * `$fromhost`, `$fromhost-ip` - DNS name and IP address of sender host
  * `$syslogfacility`, `$syslogfacility-text` - facility in numeric and text forms
  * `$syslogseverity`, `$syslogseverity-text` - same for severity
  * `$timereported` - timespamp from message
  * `$syslogtag` - `TAG` field
  * `$programname` - `TAG` field without process id: `named[12345]` -> `named`
  * whole list is [here](http://www.rsyslog.com/doc/v8-stable/configuration/properties.html)
* RuleSet contains list of rules, rule is filter and attached one or more Actions
* Filters are logical expressions using message properties. More on filters [here](http://www.rsyslog.com/doc/v8-stable/configuration/filters.html)
* Rules fro RuleSet are applied to message sequentially, it does not stop on first matched rule
* To stop message processing inside RuleSet, special discard action can be used: `stop` or `~`  for legacy format
* Inside Action templates are used often. Templates allow to generate data from message properties for using in Action. For example, message format for network forwarding or filename to write into. [More on templates](http://www.rsyslog.com/doc/v8-stable/configuration/templates.html).
* Usually Action is using ouput module("om...") or message modification module("mm..."). Here are some of them:
  - [omfile](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omfile.html) - file output
  - [omfwd](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omfwd.html) - network forwarding over udp or tcp
  - [omrelp](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omrelp.html) - network forwarding over RELP protocol
  - [onmysql](http://www.rsyslog.com/doc/v8-stable/configuration/modules/ommysql.html), [ompgsql](http://www.rsyslog.com/doc/v8-stable/configuration/modules/ompgsql.html), [omoracle](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omoracle.html) - output to database
  - [omelasticsearch](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omelasticsearch.html) - output into ElasticSearch
  - [omamqp1](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omamqp1.html) - forwarding over AMQP 1.0 protocol
  - [whole list](http://www.rsyslog.com/doc/v8-stable/configuration/modules/idx_output.html) of output modules

[More on message processing orger](http://www.rsyslog.com/doc/v8-stable/configuration/basic_structure.html#quick-overview-of-message-flow-and-objects).

## Configuration examples

Write all messages of auth and authpriv facilities into file `/var/log/auth.log` and continue processing this messages:

```bash
# legacy
auth,authpriv.*  /var/log/auth.log
# modern
if ( $syslogfacility-text == "auth" or $syslogfacility-text == "authpriv" ) then {
    action(type="omfile" file="/var/log/auth.log")
}
```

Write all messages with program name starting with "hapropxy" into file `/var/log/haproxy.log`, do not flush buffer after each message, and stop further processing:

```
# legacy (note the minus sign in front of filename - it disables buffer flush)
:programname, startswith, "haproxy", -/var/log/haproxy.log
& ~
# modern
if ( $programname startswith "haproxy" ) then {
    action(type="omfile" file="/var/log/haproxy.log" flushOnTXEnd="off")
    stop
}
# we can mix legacy and modern
if $programname startswith "haproxy" then -/var/log/haproxy.log
&~
```

Config check command: `rsyslogd -N 1`. More examples: [one](http://www.rsyslog.com/doc/v8-stable/configuration/examples.html), [two](http://wiki.rsyslog.com/index.php/Configuration_Samples).

## Client: forward logs with file names

We will save file names into `TAG` field. We want to include directories into names, not to watch single-level file mess: `haproxy/error.log`. If log is not read from file, but comes from program though standard syslog mechanism, it can reject writing `/` symbols into `TAG`, because it's against the standard. So we will encode this symbols as double underlines, and will decode back on log server.

Let's create template for transferring logs over network. We want to forward messages with tags logner than 32 symbols, because we have long meaningful log names. We want to forward pecise timestamp with timezone. Also, we will add local variable `$.suffix` to filename, I'll explain this later. Local variables in RainerScript have names starting from a dot. If variable is not defined, it will expand into empty string.

```bash
template (name="LongTagForwardFormat" type="string"
string="<%PRI%>%TIMESTAMP:::date-rfc3339% %HOSTNAME% %syslogtag%%$.suffix%%msg:::sp-if-no-1st-sp%%msg%")
```

Now let's create RuleSet to use for network message forwarding. It can be assigned for Inputs that read files, or it can be called as a function. Yep, rsyslog allows to call one RuleSet from another. To use RELP we have to load it's module first.

```bash
# http://www.rsyslog.com/doc/relp.html
module(load="omrelp")

ruleset(name="sendToLogserver") {
    action(type="omrelp" Target="syslog.example.net" Port="20514" Template="LongTagForwardFormat")
}
```


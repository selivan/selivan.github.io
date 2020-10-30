---
layout: post
title:  "Rsyslog configuration: forwarding log files with file names, handle multi-line messages, no messages lost on server downtime, failover server"
tags: [rsyslog,syslog,"multiline logs",linux]
comments_by_disqus: true
---

*This is translation of my original [article in russian](https://habrahabr.ru/post/321262/)*

{% comment %} kramdown magick https://kramdown.gettalong.org/converter/html.html#toc {% endcomment %}

* TOC
{:toc}

## Task

Forward logs to log server:
* If server is unavailable, do not lose messages, but preserve them and and send later.
* Handle multi-line messages correctly.
* For new log files client reconfiguration is sufficient, server reconfiguration is not required.
* Forward all log files with name matching wildcard, save separately on server with the same names.

Only Linux servers are used.

## Choice of software

Why use syslog in our days? We have elastic beats, logstash, systemd-journal-remote and a lot more of new shiny technologies?

* It is standard for logging in POSIX-like systems.\
Some software, like haproxy, uses only syslog. So you can not completely eliminate it
* It is used by network hardware
* It has more complex setup, but a lot more features then competitor solutions.\
For example, Elastic Filebeat still can not use inofity.
* Low memory usage. Can be used in embedded systems after [some tuning](http://wiki.rsyslog.com/index.php/Reducing_memory_usage).
* Allows to change message before saving and forwarding.\
Unusual requrement, but sometimes it's necessary. For example, [PCI DSS](https://en.wikipedia.org/wiki/PCI_DSS) in section 3.4 requires to mask or cypher card numbers, in case they are saved on disk. The nuance is: if somebody entered card number in search or contacts form, and you saved the query, you have broke the requirement.

*Observation*: users are entering card number into every input field on a page, and sometimes try to tell it together with CVV to support.

## Message format and legacy

*TLDR*: everything is broken

{% comment %} <details>
<summary> TLDR: everything is broken (click to view)</summary> {% endcomment %}
Syslog appeared in 80-x, and quickly became logging standard for Unix-like OS and network hardware. There were no standard, everybody was writing code just to be compatible with existing software. In 2001 IETF described current situation in RFC 3164(status "informational"). Implementations vary a lot, so it states "The payload of any IP packet that has a UDP destination port of 514 MUST be treated as a syslog message". Later IETF tried to create standard format in RFC 3165, but this document was inconvenient, at this moment there is no any alive software implementation. In 2009 RFC 5424 was approved, defining structured messages, but it is rarely used.
{% comment %} </details> {% endcomment %}

[Here](http://www.rsyslog.com/doc/syslog_parsing.html) you can read what rsyslog author Rainer Gerhards does think about syslog standard situation. In fact, everybody is implementing syslog as he likes, and syslog server has the task to interpret anything it receives. For example, rsyslog has [special module](http://www.rsyslog.com/doc/v8-stable/configuration/modules/pmciscoios.html) to parse format used by CISCO IOS. For the worst cases since rsyslog 5th version you can define custom parsers.

Transferred over network syslog message looks something like this:

```
<PRI> TIMESTAMP HOST TAG MSG
```

* `PRI` - priority. Calculated as `facility * 8 + severity`.
  * Facility has values from 0 to 23 for different system services: 0 - kernel, 2 - mail, 7 - news. Last 8 - from local0 to local7 - are used for services outside this predefined categories. [Complete list](https://en.wikipedia.org/wiki/Syslog#Facility).
  * Severity has values from 0(emergency, most important) to 7(debug, least important). [Complete list](https://en.wikipedia.org/wiki/Syslog#Severity_level).
* `TIMESTAMP` - time,  usually in format like `Feb  6 18:45:01`. According to RFC 3194, it also can have time format of ISO 8601: `2017-02-06T18:45:01.519832+03:00` with better precision and timezone.
* `HOST` - name of host, which generated the message
* `TAG` - contains name of program that generated the message. Not more then 32 alphanumeric characters, though in fact many implementations allow more. Any non-alphanumeric symbol stops `TAG` and starts `MSG`, colon is used usually. Sometimes can have process id in square brackets. `[ ]` are not alphanumeric, so it should be part of a message. But usually implementations consider it part of `TAG` field, and consider `MSG` start after ": " symbols
* `MSG` - message. Because of uncertainty about where `TAG` ends and it starts, often gets additional space symbol at the beginning. Can not contain new line symbols: by standard, they are frame delimeters, effectively starting new syslog message. Methods to actually transfer multi-line message:
  * escaping. On receiving side we have message with `#012` instead of new lines
  * using octet-based TCP Framing, described in RFC 5425 for TLS-enabled syslog. Non-standard, only few implementations can do it

### Alternative to syslog protocol: RELP

If messages are transferred between hosts using rsyslog, instead of plain TCP you can use [RELP](http://www.rsyslog.com/doc/relp.html) - Reliable Event Logging Protocol. It was created for rsyslog, now it's supported by some other systems. For instance, it's supported by Logstash and Graylog. Uses TCP for transport. Can optionally encrypt messages with TLS. It's more reliable than plain TCP syslog, because it does not lose messages when connection breaks. It solves problem with multi-line messages.

## Rsyslog configuration

In contrast to the second popular syslog deamon, syslog-ng, rsyslog is compatible with configs of old syslogd:

```bash
auth,authpriv.*            /var/log/auth.log
*.*;auth,authpriv.none     /var/log/syslog
*.*       @syslog.example.net
```

Because rsyslog has a lot more features than it's predecessor, config format was extended with additional directives, starting from `$` sign:

```bash
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$WorkDirectory /var/spool/rsyslog
$IncludeConfig /etc/rsyslog.d/*.conf
```

Starting with 6th version c-like RainerScript format was introduced. It allows to specify complex rules for message processing.

Because new config formats were created gradually and compatible with old format, there is a couple of flaws:
* some plugins(but I haven't seen such ones) can lack new format support, and still require old configuration directives
* configuring with old directives does not always work as expected for new format:
  * if module `omfile` is called with old format: `auth,authpriv.*  /var/log/auth.log`, then owner and group of created files are defined by old directives `$FileOwner`, `$FileGroup`, `$FileCreateMode`. And if it is called with `action(type="omfile" ...)`, then this directives are ignored and you should configure it in module loading statement or inside action itself.
  * Directives like `$ActionQueueXXX` are configuring queue used by next Action, and after their values are reset.
* semicolon is forbidden somewhere, and strictly required in other places(second happes less often).

To avoid stumbling on this flaws, one should follow this simple rules:
* for small and simple configs use old well-known format:<br />
`:programname, startswith, "haproxy"  /var/log/haproxy.log`
* for complex message processing and for fine tuning of action parameters always use RainerScript, without legacy directives like `$DoSomething`.

Read more about config format [here](http://www.rsyslog.com/doc/v8-stable/configuration/basic_structure.html#configuration-file).

## Message processing

* All messages comes from one of Inputs and fall into assigned RuleSet. If it is not set explicitly, default RuleSet will be used. All message processing directives outside separate RuleSet blocks are part of default RuleSet. For instance, all directives in traditional config format:
`local7.*  /var/log/myapp/my.log`
* Input has assigned list of message parsers. If not set explicitly, default set of parsers for traditional syslog format will be used
* Parser extracts properties from message. Some of most used:
  * `$msg` - message
  * `$rawmsg` - whole message before parsing
  * `$fromhost`, `$fromhost-ip` - DNS name and IP address of sender host
  * `$syslogfacility`, `$syslogfacility-text` - facility in numeric and text forms
  * `$syslogseverity`, `$syslogseverity-text` - same for severity
  * `$timereported` - timespamp from message
  * `$syslogtag` - `TAG` field
  * `$programname` - `TAG` field without process id: `named[12345]` -> `named`
  * complete list is [here](http://www.rsyslog.com/doc/v8-stable/configuration/properties.html)
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

Write all messages with program name starting with "haproxy" into file `/var/log/haproxy.log`, do not flush buffer after each message, and stop further processing:

```bash
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

Config check command: `rsyslogd -N 1 -f /etc/rsyslog.conf`. More examples: [here](https://www.rsyslog.com/doc/v8-stable/configuration/examples.html).

## Client: forward logs with file names

We will save file names into `TAG` field. We want to include directories into names, not to watch single-level file mess: `haproxy/error.log`. If log is not read from file, but comes from program though standard syslog mechanism, it can reject writing `/` symbols into `TAG`, because it's against the standard. So we will encode this symbols as double underlines, and will decode back on log server.

Let's create a template for transferring logs over network. We want to forward messages with tags longer than 32 symbols, because we have long meaningful log names. We want to forward precise timestamp with timezone. Also we will add a local variable `$.suffix` to the filename, I'll explain this later. Local variables in RainerScript have names starting from a dot. If variable is not defined, it will expand into empty string.

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

Now create Input to read log file, and assign it our RuleSet.

```bash
input(type="imfile"
	File="/var/log/myapp/my.log"
	Tag="myapp/my.log"
	Ruleset="sendToLogserver")
```

Note, that for every read log file rsyslog creates state files inside it's work directory(set by `$WorkDirectory`). If rsyslog can not create files in it, it will forward whole log file again after restart.

Now we have some application that uses system syslog with some tag on it's messages. We want to save this messages into local file and to forward over network:

```bash
# Template to output only message
template(name="OnlyMsg" type="string" string="%msg:::drop-last-lf%\n")

if( $syslogtag == 'nginx__access:')  then {
    # write to file
    action(type="omfile" file="/var/log/nginx/access" template="OnlyMsg")
    # forward over network
    call sendToLogserver
    stop
}
```

Last `stop` directive is required to stop processing this messages, otherwise they will get to common system syslog. Btw, if application can use socket for log messages than standard `/dev/log`(both nginx and haproxy can do this), then we can create separate Input for this socket with  [imuxsock](http://www.rsyslog.com/doc/v8-stable/configuration/modules/imuxsock.html) module and assign it to separate ruleset. So parsing whole log stream for some tags would not be required.

### Reading log files set by wildcard

*Interlude*

Programmer: Hey, I can't find logfile somevendor.log for beginning of last month on log server, could you help me?<br />
Devops: Hmmm... Are we writing such logs? You should have told me. Anyway, logrotate already have cleaned everything older than a week<br />
Programmer: @#$%^@!<br />

If application creates a lot of logs, and new ones appear often, updating configuration every time is inconvenient. I'd like to have some automation. [Imfile](http://www.rsyslog.com/doc/v8-stable/configuration/modules/imfile.html) module can read files specified by wildcards, and it saves filename in message metadata. But it saves full path, and we need only the last component, so we have to extract it. And here is the place to use the `$.suffix` variable.

```bash
input(type="imfile"
    File="/srv/myapp/logs/*.log"
	Tag="myapp__"
	Ruleset="myapp_logs"
	addMetadata="on")

ruleset(name="myapp_logs") {
    # http://www.rsyslog.com/doc/v8-stable/rainerscript/functions.html
	# re_extract(expr, re, match, submatch, no-found)
	set $.suffix=re_extract($!metadata!filename, "(.*)/([^/]*)", 0, 2, "all.log");
	call sendToLogserver
}
```

Wildcards are supported only in imfile `inotify` mode(it's default). Since version 8.25.0, wildcards are supported both in filename and path: `/var/log/*/*.log`.

### Multi-line messages

To work with files with multi-line messages imfile offers 3 options:
- `readMode=1` - messages are divided by empty string
- `readMode=2` - new messages start at rhe beginning of a line. If line starts from space or tabulation, it's part of message. Stack traces often look like this.
- `startmsg.regex` - define new message by regexp(POSIX Extended)

First two options have troubles working in `inotify` mode and third option can replace them all with right regexp, so we will use it. Reading multi-line logs have a subtlety. New message mark is often placed on the first line of the message. So we can not be sure, that last message is complete, until new one starts. Because of this last message may be never transferred. To avoid this, we set parameter `readTimeout`, and after that number of seconds last message is considered finished.

```bash
input(type="imfile"
    File="/var/log/mysql/mysql-slow.log"
    # http://blog.gerhards.net/2013/09/imfile-multi-line-messages.html
    startmsg.regex="^# Time: [0-9]{6}"
    readTimeout="2"
    # no need to escape new line for RELP
    escapeLF="off"
    Tag=" mysql__slow.log"
    Ruleset="sendToLogserver")
```

## Server

On the server we have to accept forwarded logs and save them to file tree, according to sender host IP and receive time: `/srv/log/192.168.0.1/2017-02-06/myapp/my.log`. To set log file name from message content, we can use template. Variable `$.logpath` should be set inside RuleSet before using the template.

```bash
template(name="RemoteLogSavePath" type="list") {
    constant(value="/srv/log/")
    property(name="fromhost-ip")
    constant(value="/")
    property(name="timegenerated" dateFormat="year")
    constant(value="-")
    property(name="timegenerated" dateFormat="month")
    constant(value="-")
    property(name="timegenerated" dateFormat="day")
    constant(value="/")
    property(name="$.logpath" )
}
```

Let's load all necessary modules and turn off `$EscapeControlCharactersOnReceive`, otherwise we will have `\n` instead of new lines in received messages.

```bash
# Accept RELP messages from network
module(load="imrelp")
input(type="imrelp" port="20514" ruleset="RemoteLogProcess")

# Default parameters for file output. Old-style global settings are not working with new-style actions
module(load="builtin:omfile" FileOwner="syslog" FileGroup="adm" dirOwner="syslog"
        dirGroup="adm" FileCreateMode="0640" DirCreateMode="0755")

# Module to remove 1st space from message
module(load="mmrm1stspace")

# http://www.rsyslog.com/doc/v8-stable/configuration/input_directives/rsconf1_escapecontrolcharactersonreceive.html
# Print recieved LF as-it-is, not like '\n'. For multi-line messages
# Default: on
$EscapeControlCharactersOnReceive off
```

Now let's create RuleSet tp parse incoming messages and saving them to apropriate files and folders. Services relying on syslog are expecting, that it will save message time and other syslog fields. So messages with standard facilities are saved in syslog format. For messages with local0-local7 facilities we will generate filename from `TAG`, and save pure message without other syslog fields. Problem with extra space in front of message is still present, because it emerges in message parsing phase. We will cut it out.

To improve performance we will use asynchronous write: `asyncWriting="on"` and large buffer: `ioBufferSize=64k`. We won't flush the  buffer after each received message: `flushOnTXEnd="off"`, but we will flush it once a second to have fresh logs on log server: `flushInterval="1"`.

```bash
ruleset(name="RemoteLogProcess") {
    # For facilities local0-7 set log filename from $programname field: replace __ with /
    # Message has arbitary format, syslog fields are not used
    if ( $syslogfacility >= 16 ) then
    {
        # Remove 1st space from message. Syslog protocol legacy
        action(type="mmrm1stspace")

        set $.logpath = replace($programname, "__", "/");
        action(type="omfile" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="OnlyMsg"
        flushOnTXEnd="off" asyncWriting="on" flushInterval="1" ioBufferSize="64k")

    # Logs with filename defined from facility
    # Message has syslog format, syslog fields are used
    } else {
        if (($syslogfacility == 0)) then {
    	    set $.logpath = "kern";
        } else if (($syslogfacility == 4) or ($syslogfacility == 10)) then {
            set $.logpath = "auth";
        } else if (($syslogfacility == 9) or ($syslogfacility == 15)) then {
            set $.logpath = "cron";
        } else {
            set $.logpath ="syslog";
        }
        # Built-in template RSYSLOG_FileFormat: High-precision timestamps and timezone information
        action(type="omfile" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="RSYSLOG_FileFormat"
        flushOnTXEnd="off" asyncWriting="on" flushInterval="1" ioBufferSize="64k")
    }
} # ruleset
```

## Reliable message delivery. Queues.

![rsyslog message flow schema](https://habrastorage.org/files/531/96b/eb1/53196beb160c48baa0e52ee3472439a5.jpg)

*image from blog [k-max.name](http://www.k-max.name/linux/rsyslog-na-debian-nastrojka-servera/)*

For some Actions execution can sometimes slow down or stop, for example forwarding over network or writing to database. To prevent message loss and to not affect other Actions, we can use [queues](http://www.rsyslog.com/doc/v8-stable/concepts/queues.html). Each Action always have assigned queue, by default it's zero size Direct Queue. Also we have common main queue for all messages from all Inputs, it's parameters also can be tuned.

Queue types: disk, in-memory and most interesting option: Disk-Assisted Memory Queues. Latter ones use memory and start using disk, if memory have too much messages or to save unprocessed messages on service restart. Queue will start saving messages to disk when their number reaches `queue.highwatermark`, and on `queue.lowwatermark` it stops saving messages on disk. To save unprocessed messages on service restart, we should specify `queue.saveonshutdown="on"`.

If network forwarding or writing to database was unsuccessful, Action is suspended. rsyslog will try to resume Action after some interval, this interval is increased with every failed attempt. To start sending logs after server became available: set `action.resumeRetryCount="-1"` (unlimited) and small suspend interval: `action.resumeInterval="10"`. More on [action parameters](http://www.rsyslog.com/doc/v8-stable/configuration/actions.html).

RuleSet for client with queue looks like this:

```bash
ruleset(name="sendToLogserver") {
    # Queue: http://www.rsyslog.com/doc/v8-stable/concepts/queues.html#disk-assisted-memory-queues
    # Disk-Assisted Memory Queue: queue.type="LinkedList" + queue.filename
    # queue.size - max elements in memory
    # queue.highwatermark - when to start saving to disk
    # queue.lowwatermark - when to stop saving to disk
    # queue.saveonshutdown - save on disk between rsyslog shutdown
    # action.resumeRetryCount - number of retries for action, -1 = eternal
    # action.resumeInterval - interval to suspend action if destination can not be connected
    # After each 10 retries, the interval is extended: (numRetries / 10 + 1) * Action.ResumeInterval
    action(type="omrelp" Target="syslog.example.net" Port="20514" Template="LongTagForwardFormat"
    queue.type="LinkedList" queue.size="10000" queue.filename="q_sendToLogserver" queue.highwatermark="9000"
    queue.lowwatermark="50" queue.maxdiskspace="500m" queue.saveonshutdown="on" action.resumeRetryCount="-1"
    action.reportSuspension="on" action.reportSuspensionContinuation="on" action.resumeInterval="10")
}
```

Now we can easily reboot log server - messages on client will be saved in queue and forwarded later.

**WARNING:** Message relative order can be disrupted on message transfer from queue after resuming network connectivity(thanks [zystem](https://habrahabr.ru/users/zystem/) for the [comment](https://habrahabr.ru/post/321262/#comment_10058004)). Rsyslog author [replied](https://github.com/rsyslog/rsyslog/issues/1400#issuecomment-278396567) that it is expected behaviour, details can be found here: [LinuxKongress2010rsyslog.pdf](http://www.gerhards.net/download/LinuxKongress2010rsyslog.pdf) (section 7 "Concurrency-related Optimizations"). Briefly: attempt to preserve strict message order for multi-threaded processing leads to performance loss because of thread locks; notion of strict message order can have no sense for some of transport types, for multi-thread message generators and receivers.

## Failover

Action can be configured to execute only if previous Action is suspended: [description](http://www.rsyslog.com/action-execonlywhenpreviousissuspended-preciseness/). This make failover configurations possible. Some Actions use transaction to improve performance. If they do, success or failure will be known only after transaction is finished, when messages are already processed. So some messages can be lost without calling failover Action. To prevent this, we should set parameter `queue.dequeuebatchsize="1"`(default: 16). It can hit performance.

```bash
ruleset(name="sendToLogserver") {
    action(type="omrelp" Target="syslog1.example.net" Port="20514" Template="LongTagForwardFormat")
    action(type="omrelp" Target="syslog2.example.net" Port="20514" Template="LongTagForwardFormat"
    action.execOnlyWhenPreviousIsSuspended="on" queue.dequeuebatchsize="1")
}
```

I haven't use this failover config on production.

## Logrotate interaction

### Logs written by rsyslog itself

Can be rotated perfectly well with default scheme: `smth.log` is renamed to `smth.log.1` and new `smth.log` is created. In post-rotate action you should send SIGHUP to rsyslogd process. **Note**: rsyslog does not reload configuration on SIGHUP, it just re-opens all log files.

```bash
/var/log/someapp/*.log{
    weekly
    missingok
    rotate 5
    create 0644 syslog adm
    sharedscripts
    postrotate
        test -s /run/rsyslogd.pid && kill -HUP $(cat /run/rsyslogd.pid)
        # postrotate script should always return 0
        true
    endscript
}
```

### Logs written by application and read by rsyslog

For application that can re-open files on request(SIGHUP or something alike) no additional configuration is required: rsyslog will notice file inode change and re-open it.

Problems appear with logrotate `copytruncae` option, that truncates `smth.log` to zero after  creating copy `smth.log.1`. rsyslog just stops reading lines from that file. Starting from version 8.16.0, imfile module has option `reopenOnTruncate` (default `"off"`, to enable switch to `"on"`). This option tells rsyslog to reopen input file on truncate(inode unchanged but file size on disk is less than current offset in memory). It is marked as "experimental", but works fine for me in production. For versions older than 8.16.0, you can fix `copytruncate` rotating by sending SIGHUP to rsyslogd process in post-rotate action.

*Note*: On Debian/Ubuntu systems by default logrotate output and result is not saved anywhere, so you won't notice if it's broken. I recommend to fix this in `/etc/cron.daily/logrotate`.

## Summary

IMHO I created rather flexible and convenient configuration. Logs are forwarded from both files and syslog. Multi-line messages are forwarded correctly. Log server restart does not cause losing messages. To add new log files, only client should be re-configured, server stays as it is.

This works on rsyslog v8, I didn't check it on earlier version. For Ubuntu there is official ppa [adiscon/v8-stable](https://launchpad.net/~adiscon/+archive/ubuntu/v8-stable). For CentOS/RHEL you can use [official repository](http://www.rsyslog.com/rhelcentos-rpms/).

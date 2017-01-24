---
layout: post
title:  "Dynamically generate log name from syslog tag on rsyslog server"
tags: [rsyslog, syslog]
---

Here is convenient and flexible setup of syslog server with rsyslog. It dynamically generates log filename from syslog message tag, so no modification is required on server if new log type is added.

TODO: wildcards:
* http://www.rsyslog.com/doc/master/configuration/modules/imfile.html#metadata
* %$!metadata!filename%
TODO: multiline messages
TODO: queue for performance
TODO: failover - 2 servers

Some traditional unix applications, like cron, sshd and linux kernel itself, rely on syslog(3) system call for generating log messages. Their messages do not include timestamp, because syslog server generates it for recieved message. Other applications write log files directly on disk, where rsyslog can pick them with `imfile` module. For this applications we will save log filename to message tag.

Rsyslog workflow
================

* Syntax - old and new(RainerScript).
* Inputs
* Rulesets. Default ruleset
* Templates

Client setup
============

/etc/rsyslog.conf:


```bash
...
# RSYSLOG_FileFormat: High-precision timestamps and timezone information
$ActionFileDefaultTemplate RSYSLOG_FileFormat
...
```

/etc/rsyslog.d/myapp.conf:

```bash
input(type="imfile" File="/var/log/myapp/error.log" Tag="myapp__error" ruleset="myapp__error")
ruleset(name="myapp__error") {
    action(type="omfwd" Target="192.168.0.1" Port="5143" Protocol="tcp")
}
```

/etc/rsyslog.d/zz-remote-common.conf:

```bash
*.*  @@192.168.0.1:514
```


Sever setup
===========

/etc/rsyslog.conf:

```bash
...
# RSYSLOG_FileFormat: High-precision timestamps and timezone information
$ActionFileDefaultTemplate RSYSLOG_FileFormat
...
```

/etc/rsyslog.d/00-collect-remote-logs.conf:

```bash
template(name="RemoteLogSavePath" type="list") {
        constant(value="/srv/logs/")
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

template(name="OnlyMsg" type="string" string="%msg:::drop-last-lf%\n")
template(name="Debug" type="string" string="%syslogfacility%.%syslogpriority% %syslogfacility-text%.%syslogpriority% %programname% %msg:::drop-last-lf%\n")

# Accept syslog messages on port 514 and process with given ruleset
module(load="imtcp")
input(type="imtcp" port="514" ruleset="RemoteLogProcess")

# omfile is always loaded as built-in module, here we can set parameters
#module(load="builtin:omfile")

# 0 kern
# 1 user
# 4 auth
# 10 authpriv
# 9 clock daemon - cron
# 15 cron
# 16-23 local0-7
ruleset(name="RemoteLogProcess") {
        if (($syslogfacility == 0)) then {
                set $.logpath = $syslogfacility-text;
        } else if (($syslogfacility == 4) or ($syslogfacility == 10)) then {
                set $.logpath = "auth";
        } else if (($syslogfacility == 9) or ($syslogfacility == 15)) then {
                set $.logpath = "cron";
        } else if ($syslogfacility < 16) then {
                set $.logpath ="syslog";
        # For facilities local0-7 set log file name from $programname field
        # Replace __ with /
        # Send meaasge and stop futher processing
        } else {
                set $.logpath = replace($programname, "__", "/");
                action(type="omfile" ioBufferSize="64k" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="OnlyMsg")
                & stop
        }

        # Possible omfile tuning: flushOnTXEnd="off" asyncWriting="on"
        # RSYSLOG_FileFormat: High-precision timestamps and timezone information
        action(type="omfile" ioBufferSize="64k" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="RSYSLOG_FileFormat")
}
```

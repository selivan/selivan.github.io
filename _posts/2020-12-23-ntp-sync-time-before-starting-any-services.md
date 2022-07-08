---
layout: post
title:  "Syncronize time by NTP before starting any services in Linux"
tags: [ ntp, chrony, systemd ]
comments_by_utterance: true
---

Servers often have wrong clock on startup. NTP services, like `ntp`, `chrony` and `systemd-timesyncd` try to correct clock gradually to avoid weird bugs in software. Therefore, if server has a large clock offset on startup, it works with incorrect clock for several minutes.

In my experience, AWS instances may have clock error up to 5 minutes on startup. Server writing log timestamps 5 minutes in the past or in the future is not always a good idea.

Solution is to force NTP time syncronization once before starting any other services. I prefer to use [chrony](https://chrony.tuxfamily.org/): it can act both as always runnig NTP client and one-time syncronization tool; `chronyc` clearly reports syncronization status, making it easy to monitor; it is [recommended by AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html).

All other services in `multi-user.target` will start after time is syncronized or failed to syncronize after given timeout.

`/etc/systemd/system/ntp-sync-once.service` :

{% highlight ini %}
[Unit]
Description=Quick sync NTP one time and exit

Wants=network-online.target
After=network-online.target

Before=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=True
# Ugly workaround for not working properly network-online.target
ExecStartPre=sh -c "while ! ip -4 r | grep ^default; do echo waiting for ipv4 default route to appear; sleep 0.5; done"
# -t <timeout in seconds>  timeout after which chronyd will exit even if clock is not syncronized
ExecStart=/usr/sbin/chronyd -q -t 20

[Install]
WantedBy=multi-user.target
{% endhighlight %}

`network-online.target` sometimes is [not working as expected](/2020/12/23/systemd-broken-network-online-target-workaround.html), `ExecStartPre` line is a workaround for that.

{% comment %}

FIXME:

Wants=network-online.target

leads to

```
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: Stopped Quick sync NTP one time and exit.
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found ordering cycle on network-online.target/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found dependency on network.target/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Found dependency on chrony-ntp-sync-once.service/start
Jan 02 08:21:53 ubuntu2004.localdomain systemd[1]: chrony-ntp-sync-once.service: Job network-online.target/start deleted to break ordering cycle startin>
```

{% endcomment %}

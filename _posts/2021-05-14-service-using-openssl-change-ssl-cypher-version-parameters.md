---
layout: post
title:  "Change TLS/SSL version and cypher parameters for Linux service using openssl library"
tags: [ openssl, ssl, tls, systemd ]
comments_by_utterance: true
---

Sometimes you need to change TLS/SSL parameters for a service using `libssl` library from [openssl](https://www.openssl.org/), but the service config does not accept that parameters. In this example, I had to change rsyslog forwarder parameters to send logs to the target that wasn't playing nice with TLS 1.3 and modern encryption protocols.

`libssl` and applications using it take configuration parameters from configuration file set by environment variable `OPENSSL_CONF` or from default file `/etc/ssl/openssl.cnf`. 

Openssl documentation is not the easiest one to read, but `man 5ssl config` and some googling got me what I wanted.

`/etc/ssl/openssl.no-tls13.cnf`:

{% highlight ini %}
# This definition stops the following lines choking if HOME isn't
# defined.
HOME                    = .

openssl_conf = default_conf

[default_conf]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
MaxProtocol = TLSv1.2
CipherString = DEFAULT@SECLEVEL=1

{% endhighlight %}

`/etc/systemd/system/rsyslog.service.d/override-openssl-params.conf`:

{% highlight ini %}
[Service]
Environment="OPENSSL_CONF=/etc/ssl/openssl.cnf.no-tls13"
{% endhighlight %}

And finally applying the new configuration:

{% highlight shell %}
systemctl daemon-reload
systemctl restart rsyslog
{% endhighlight %}

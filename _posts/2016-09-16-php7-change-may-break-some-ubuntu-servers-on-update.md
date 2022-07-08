---
layout: post
title:  "Change in PHP 7 that may break some of Ubuntu servers on update"
tags: [php,ubuntu]
redirect_from: "/2016/08/16/php7-change-may-break-some-ubuntu-servers-on-update.html"
comments_by_utterance: true
---
*This is translation of my original article in russian: [https://habrahabr.ru/post/310136](https://habrahabr.ru/post/310136)*

[http://php.net/manual/en/configuration.file.php#configuration.file.changelog](http://php.net/manual/en/configuration.file.php#configuration.file.changelog):

> 7.0.0 Hash marks (#) are no longer recognized as comments.

Seems harmless. Administrators will see errors on test installation and fix old configs. But here comes one nasty trait of php-fpm: it refuses to start with incorrect `php-fpm.conf`, but it will start with incorrect `php.ini`, ignoring all settings there just rolling back to default values. Error is not written to php-fpm log. It can be spotted in console, but service start script hides that messages.

If `php.ini` was copied from 5th version, and more strict parser of 7th reads it with errors - php-fpm will silently work with default values. For example, if old file had `#` for comments and some of that comments has a brace `(` inside. Without brace it still allows such comments, despite what changelog says.

Maximum size of uploaded file becomes `post_max_size=8m`. `expose_php` in on, so PHP version is sent out in `X-Powered-By` header. `disable_functions`, used to restrict potentially dangerous functions, becomes empty. `display_errors` is 1 and visitors will see a full stacktrace on error pages. And a lot of other funny things.

Ubuntu maintainers are trying to avoid this problem with a kludge:

```
/etc/systemd/system/multi-user.target.wants/php7.0-fpm.service:

...
ExecStartPre=/usr/lib/php/php7.0-fpm-checkconf
...

/usr/lib/php/php7.0-fpm-checkconf:

...
errors=$(/usr/sbin/php-fpm7.0 --fpm-config "$CONFFILE" -t 2>&1 | grep "\[ERROR\]" || true);
...
```

But the kludge doesn't work:

```
root@xenial:~# /usr/sbin/php-fpm7.0 --fpm-config  /etc/php/7.0/fpm/php-fpm.conf --test
PHP:  syntax error, unexpected '(' in /etc/php/7.0/fpm/php.ini on line 6
[14-Sep-2016 14:24:46] NOTICE: configuration file /etc/php/7.0/fpm/php-fpm.conf test is successful

root@xenial:~# /usr/lib/php/php7.0-fpm-checkconf; echo $?
0
```

php7.0-fpm package from popular [ppa:ondrej/php](https://github.com/oerdnj/deb.sury.org/issues/456), often used to deliver PHP 7 to Ubuntu trusty and precise servers, does not have this check at all.

In total: if you are upgrading from PHP 5 tp PHP 7, make sure, that is does not ignore settings in `php.ini` and use default values.

P.S.

  * [bug for ppa:ondrej/php](https://github.com/oerdnj/deb.sury.org/issues/456)
  * [bug for php7.0-fpm in ubuntu xenial](https://bugs.launchpad.net/ubuntu/+source/php7.0/+bug/1623540)
  * [bug for php developers](https://bugs.php.net/bug.php?id=73099)

---
layout: post
title:  "Make notify-send work from user cron file in ubuntu"
tags: [cron,notify-send,desktop,ubuntu]
comments_by_utterance: true
---
  In ubuntu, you can use `notify-send` to show notificactions. But if you try to show notification from crontab, it will fail: `notify-send` requires proper values in `$DBUS_SESSION_BUS_ADDRESS` and `$DISPLAY`. To override this disappointing limitation, you can grep this values from some known process of yours. Here is example that works for XFCE, Gnome, Unity, Cainnamon and KDE:

`/usr/local/bin/gui-program-from-cron.sh`:

```bash
#!/bin/sh
[ "$#" -lt 1 ] && echo "Usage: $0 program options" && exit 1

program="$1"
shift

user=$(whoami)
env_reference_process=$( pgrep -u "$user" xfce4-session || pgrep -u "$user" ciannamon-session || pgrep -u "$user" gnome-session || pgrep -u "$user" gnome-shell || pgrep -u "$user" kdeinit | head -1 )

export DBUS_SESSION_BUS_ADDRESS=$(cat /proc/"$env_reference_process"/environ | grep --null-data ^DBUS_SESSION_BUS_ADDRESS= | sed 's/DBUS_SESSION_BUS_ADDRESS=//')
export DISPLAY=$(cat /proc/"$env_reference_process"/environ | grep --null-data ^DISPLAY= | sed 's/DISPLAY=//')
"$program" "$@"
```

`crontab`:

```config
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
*/45 * * * * /usr/local/bin/gui-program-from-cron.sh notify-send --expire-time=30000 --icon=dialog-information "GET UP AND EXERCISE"
```

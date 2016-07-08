---
layout: post
title:  "Make notify-send work from user cron file in ubuntu"
tags: notify-send,ubuntu,desktop
---
In ubuntu, you can use `notify-send` to show notificactions. But if try to show notification from crontab, it will fail: `notify-send` requires proper values in `$DBUS_SESSION_BUS_ADDRESS` and `$DISPLAY`. To override this disappointing limitation, you can grep this values from some known process of yours. Here is example for XFCE:

`/usr/local/bin/notify-send-from-cron.sh`:

```
#!/bin/sh
[ "$#" -lt 2 ] && echo "Usage: $0 delay_in_microseconds notification_text" && exit 1

delay=${1:-2000}
shift 1
env_reference_process=xfce4-session
user=$(whoami)

export DBUS_SESSION_BUS_ADDRESS=$(cat /proc/$(pgrep -u $user $env_reference_process)/environ | grep -z DBUS | sed 's/DBUS_SESSION_BUS_ADDRESS=//')
export DISPLAY=$(cat /proc/$(pgrep -u $user $env_reference_process)/environ | grep -z DISPLAY | sed 's/DISPLAY=//')
notify-send --expire-time="$delay" --icon=dialog-information "$*"
```

`crontab`:

```
*/5 * * * * /home/selivan/bin/notify-send-from-cron.sh 6000 "BLINK EYES"
*/45 * * * * /home/selivan/bin/notify-send-from-cron.sh 30000 "GET UP AND EXERCISE"
```

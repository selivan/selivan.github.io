---
layout: post
title:  "Add custom display resolution in LightDM"
tags: [lightdm,xrandr,desktop,ubuntu]
comments_by_disqus: true
---

Sometimes Xorg doesn't detect all possible valid resolutions for a display.

For example: Lenovo YOGA 900-13ISK has HiDPI 13.3" display with resolution 3600x1800. I don't need HiDPI on such a small screen - my shortsightedness makes it pointless :) So logical step is to set resolution to 1600x900 - each point will be precisely 4 pixels and the image will remain sharp. Unfortunately, available options are 1600x1200(blurred image), 1600x1024(blurred image) and then 1440x900(place on the sides is not used). Let's fix this.

Script to add display resolution `/etc/lightdm/add-and-set-resolution.sh`:

```bash
#!/bin/bash
set -x

output="$1"
x="$2"
y="$3"
freq="$4"

if [ $# -ne 4 ]; then
echo "Usage: $0 output x y freq"
echo "To find output name: xrandr -q"
exit 0
fi

mode=$( cvt "$x" "$y" "$freq" | grep -v '^#' | cut -d' ' -f3- )
modename="${x}x${y}"

xrandr --newmode $modename $mode
xrandr --addmode "$output" "$modename"
xrandr --output "$output" --mode "$modename"

# Always return success or lightdm goes into infinite loop
exit 0
```

Find out what our display name is: `xrandr -q`. For Lenovo Yoga 900 it is "eDP-1". And now add this script to lightdm:

`/etc/lightdm/lightdm.conf.d/50-display-setup-script.conf`:

```ini
[Seat:*]
display-setup-script=/etc/lightdm/add-and-set-resolution.sh eDP-1 1600 900 60
```

Voila! Now we have required resolution available.

How it works:
 * Lightdm hook `display-setup-script` is run as root after X starts before user session/greeter.
* `cvt` calculates VESA Coordinated Video Timing modes and returns correct X modelines.
* `xrandr` adds modeline to server, then adds that mode to list of valid modes for the output, and swithes to it.
* script should always return success, even if it failed to add new mode - otherwise lightdm will go into infinite restart cycle

Links:
 * [askubuntu.com/a/377944/25924](https://askubuntu.com/a/377944/25924)
 * [wiki.ubuntu.com/LightDM](https://wiki.ubuntu.com/LightDM)

---
layout: post
title:  "Auto-resize screen in Virtualbox guest Linux system"
tags: [virtualbox, desktop, screen resolution]
comments_by_utterance: true
---

**UPDATE**: There is an alternative solution from @vitalyrepin for VBoxSVGA controller, see it in comments.

**NOTE**: This post is actual for VirtualBox 5.x - 6.0, and may be later releases.

To enable auto-resizing screen resolution for Linux guest you should use the VBoxVGA virtual graphics controller(Machine Settings - Display - Graphics Controller).

This is a tricky part, because "Create Virtual Machine" dialog by default chooses the VMSVGA controler for new Linux machines.

Documentation [says](https://www.virtualbox.org/manual/ch03.html#settings-screen) that VBoxSVGA is the best controller type with improved performane, but for me screen auto-resize doesn't work with it either.

And of course, you should install virtualbox guest utils and video drivers on the guest host. For Ubuntu/Debian they are in this packages:

```
sudo apt install virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11
```

Or, if you use the [HWE](https://wiki.ubuntu.com/Kernel/LTSEnablementStack) kernel:

```
sudo apt install virtualbox-guest-dkms-hwe virtualbox-guest-utils-hwe virtualbox-guest-x11-hwe
```

Now reboot the guest and screen auto-resizing(View - Auto-resize guest display) will work fine.

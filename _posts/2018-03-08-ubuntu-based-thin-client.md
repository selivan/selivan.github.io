---
layout: post
title:  "Ubuntu based thin client made with your own hands"
tags: [ubuntu,pxe,thinclient]
comments_by_disqus: true
---

**NEWS**: [Now](https://github.com/selivan/thinclient/commit/2e0ad63404027dfdcdb0b997a0b6c7d382048f86) this project supports Ubuntu 20.04 Focal Fossa (LTS release) and offers an option to use VMWare Horizon, besides FreeRDP.

*This article in russian: [habrahabr.ru/post/350780](https://habrahabr.ru/post/350780/)*

![logo ubuntu plus windows](/images/2018-03-08-ubuntu-based-thin-client/ubuntu-and-windows-250x250.jpg)

*Image from [getwallpapers.com](http://getwallpapers.com/collection/kali-linux-desktop-wallpaper)*

## History

Long ago in 2013 one bank used custom thin clients based on [DisklessUbuntu](https://help.ubuntu.com/community/DisklessUbuntuHowto). Thay had some problems, if I remember it right, mounting root file system over network did not work very well in large offices with laggy network. My good friend [@efim-a-efim](https://github.com/efim-a-efim) created first version of thin client, that could boot completely into RAM, without mounting anything over network.

Then I worked with that project. It had a lot of custom features, specific for our use case. Then the bank was closed(it's license was revoked),  source codes for the client were moved to my github: [thunclient](https://github.com/selivan/thinclient). A couple of times I modified it for a bit of money.

Recently I got time to make this pile of ugly unreliable scripts into pretty convenient and easy-to-use solution:

* Vagrant brings up virtual machine, that can be configured as ordinary workstation
* Single script builds files for network boot, all unnecessary parts are cut out
* Vagrant brings up virtual PXE server and network boot client to test the resulting build

## What it can do

* Boots entirely into RAM, does not require to mount root FS over network
* Ubuntu-based, you can find almost any software in it's reach repositories, or connect external of you miss something. Particularly good part is that security updates arrive in Ubuntu repositories fast enough.
* It can mount additional overlays on top of root FS.  You can add some custom software only for some workstations without building a new image
* It uses [zram](https://www.kernel.org/doc/Documentation/blockdev/zram.txt) - memory compression, it's good for old clients with a small amount of RAM. Although it is not bad for modern clients as well.
* Out of the box light desktop (LXDE) with an RDP client is build. RDP servers addresses and options are simply passed from PXE server in boot parameters.
* You can change single parameter in config and the minimal console system will be built. It's a good basis for your own custom build.
* If boot failed because of server or network problem, it will briefly display an error message and start over. It's convenient that when problems are fixed, workstations will start themselves without manual interaction.

In the bank we used VNC to connect to user's thin client(it was `x11vnc` to connect to running Xorg session). This is not required for anyone(usually it is enough to connect to user's RDP session on a terminal server), and convenience/security requirements differ a lot for different environments. Therefore, I did not include that part.

## Alternatives

* [Thinstation](http://www.thinstation.org/)

Well, if Thinstation completely satisfies your requirements - you would better use it, it's older and more mature project. Plus it is about one and a half times smaller in size, because it is specially crafted for minimal size, not just slightly modified standard Ubuntu.

But it has ancient versions of software, and not a lot of it. If you need something special, not just client for RDP/Citrix/..., you would have to build it yourself, and do so for each update.

* [LTSP](http://ltsp.org/)

As [kvaps](https://habrahabr.ru/users/kvaps/) pointed out in [comment](https://habrahabr.ru/post/350780/#comment_10702986) to russian article, LTSP can copy squashfs image into RAM and work without mounting FS over network: variable [LTSP_NBD_TO_RAM](https://github.com/kvaps/ltsp/blob/master/client/Debian/share/initramfs-tools/scripts/init-bottom/ltsp#L31) controls it. It uses chroot for configuration, which may be less convenient, especially for configuring GUI enviromment and applications. It is also a good mature project, you may consider it as an alternative.

## Vagrant vs chroot

Previous versions used chroot, like most of similar projects do, Thinstation for example. It is easy, but program running in chroot is not exactly the same as program running on real or virtual machine: there is no interaction with system init, with other programs and services. And Vagrant made the build process as simple as possible: you just configure a virtual machine like you do for real one, and that's it.

Of course, using Vagrant brings some difficulties.

The `virtualbox-guest-utils` service should be running on the virtual machine, for shared folders to work. In addition, you need a boot manager(`grub`), mandatory for a machine with disk and useless for network boot client. I solved this problems by excluding this packages files from build, so they do not affect the size of resulting image.

Besides, Vagrant requires working ssh, that allows login for a user with Vagrant generated key. I exclude the vagrant user's home folder with that key. You can put ssh key for ubuntu user - that one is used for work - into it's home directory.

And Vagrant generates network interfaces configuration, that won't work on real machine. So I have to swap `interfaces` file during the build, and I created a script, that on real machine generates `interfaces` config with all available interfaces configured with DHCP.

Provisioning is done with Ansible. It is very convenient tool to configure all kinds of software and hardware. But I didn't want to include Ansible and python2 that is requires into the resulting image: useless waste of space. Installing Ansible on the real machine, that runs Vagrant and VirtualBox, is also a bad option: this will complicate the build process.

Vagrant allows you to make a trick: install Ansible on one virtual(test PXE server), and provision other virtuals from it. To do so, the virtuals should have static IP addresses. Well, we already solved the interfaces configuration problem.

## The naughty squash

[Squashfs](https://en.wikipedia.org/wiki/SquashFS) is compressing read-only filesystem. It is used in most of existing Linux LiveCD. It allows you to create a fairly compact system image, located inside the RAM.

A lot of things should be cut of the resulting image:  `/tmp`, `/run`, `/proc`, `/sys`, `/usr/share/doc` and so on.

Utility `mksquashfs` supports as many as 3 types of lists to exclude files: by full path, by masks and by regular expressions. It would seem that everything is fine. But last two options do not support paths starting with `/`. I could not exclude files inside some directory without excluding the directory itself.

I got tired of fighting with it, so I just use `find` to find files and directories to exclude, and put it all into a single huge file with full paths. Ugly_crutch.jpg. But it works. The only artifact for this approach is the lonely directory `/proc/NNN`, corresponding to mksquashfs process id, which did not exist when the exclude list was created. procfs is anyway mounted on top of it.

## Initrd magic

In order not to drag inside kernel all required drivers and an logic for mounting the root FS, Linux uses initial ramdisk. Previously, the initrd format was used, in which the disk was an actual filesystem image. A new format appeared in 2.6 kernel - initrams, which is cpio archive extracted to tmpfs. Both initrd and initrams can be compressed to save the loading time. A lot of tools and filenames still mention initrd, though it is not used anymore.

Debian/Ubuntu uses package initramfs-tools to create initramfs. It provides the following customization options:

* hooks - special format scripts, that allow you to add kernel modules and executable files with all required libraries.
* scripts inside directories `init-bottom`, `init-premount`, `init-top`, `local-block`, `local-bottom`, `local-premount`, `local-top`, executed in appropriate time on boot. See [man initramfs-tools(8)](http://manpages.ubuntu.com/manpages/xenial/en/man8/initramfs-tools.8.html).
* the most interesting option - you can add your own boot scripts, that mount the root FS. This scripts should define shell function `mountroot()`, which will be used by the main script `/init`. initramfs-tools already includes script `local` to mount root FS on local drive and `nfs` to mount root FS over network. Use script is selected by the boot parameter `boot`.

So, to mount the root FS in some tricky way, you have to create your own boot script, define function `mountroot()` in it, pass this script name in boot parameter `boot`. And don't forget to write hooks that will include into initramfs all required kernel modules and executables.

## Overlays

To create a single root filesystem from multiple [OverlayFS](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt) is used. First versions used AUFS(it is used by the most of Linux LiveCD). But it was not accepted into the mainline kernel, and now everybody is advised to switch to OverlayFS.

After mounting the real root FS into directory inside initramfs, the program `run_init` from `klibc-utils` will be launched. It will check that root FS is mounted inside initramfs, clear the initramfs(why should we waste memory for it?), move mount point of root FS into `/` and launch the system init. [Some details](https://askubuntu.com/a/910374/25924). This program is build as a separate executable file, because a script using external tools will break after cleaning the initramfs.

If root FS is assembled from several overlays, mounted inside initrams, after running `run_init` this mount points will disappear and it will be broken. To avoid this, we can move overlay mount points **inside** the root FS, where they will be safe. Recursion :) This is how we do it: `mount --move olddir newdir`.

I had to disable AppArmor: it's profiles re designed to work with root FS directly mounted from a single device. When OverlayFS is used, AppArmor recognizes that `/sbin/dhclient` is really `/AUFS/root/sbin/dhclient`, and the profile is broken. The only way to use it is to rewrite profiles for all application, and update each time thay change.

## Where the write support is required

Generally, Linux can work fine when all FS are mounted read-only. But many programs rely on ability to write something on disk, so you have to mount tmpfs to this paths:

* `/tmp`, `/var/tmp` - that's obvious
* `/var/log` - write some logs
* `/run` - almost all services won't run without it
* `/media` - mount connected media
* `/var/lib/system` - it is used by a lot of programs from `systemd`, for example `systemd-timesyncd`
* `/var/lib/dhclient` - this is where dhclient writes leases information
* `/etc/apparmor.d/cache` - if you manage to use AppArmor, it will need to write files inside `/etc`. IMHO this is disgusting, they should use `/var` for that.

## Summary

If you would like to build and Ubuntu image that boots over network and works entirely from RAM - here you can get a convenient ready-to-use construction kit: [thinclient](https://github.com/selivan/thinclient). I would be happy too see any feedback here in comments or on github.

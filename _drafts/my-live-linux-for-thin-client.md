---
layout: post
title:  "Ubuntu based thin client made with your own hands"
tags: [ubuntu,pxe,thinclient]
---

<!-- *This article in russian: [https://habrahabr.ru/](habrahabr.ru/)* -->

## History

Far in 2013 one bank used custom thin clients based on [DisklessUbuntu](https://help.ubuntu.com/community/DisklessUbuntuHowto). Thay had some problems, if I remember right mounting root file system over network did not work very well in large offices with weak network. My good friend [@deadroot](https://habrahabr.ru/users/deadroot/) created first version of thin client, that could boot completely into RAM, without requiring something to be mounted over network.

Then I worked with that project. It had a lot of custom features, specific for our use case. Then the bank was closed(it's licence was revoked),  source codes for the client were moved to my github: [thunclient](https://github.com/selivan/thinclient). A couple of times I modified it for a bit of money.

Recently I got time to make this pile if ugly unreliable scripts into pretty convenient and easy-to-use solution:

* Vagrant brings up virtual machine, that can be configured as ordinary workstation
* Single script builds files for network boot, all unnecessary parts are cut out
* Vagrant brings up virtual PXE server and network boot client to test the resulting build

## What it can do

* Boots entirely into RAM, does not require to mount root FS over network
* Ubuntu-based, you can find almost any software in it's reach repositories, or connect external of you miss something. Particularly good part is that security updates arrive in Ubuntu repos fast enough.
* It can mount additional overlays on top of root FS.  You can add some custom software only for some workstations without building a new image
* It uses [zram](https://www.kernel.org/doc/Documentation/blockdev/zram.txt) - memory compression, it's good for old clients with a small amount of RAM. Although it is not bad for modern clients as well.
* Out of the box light desktop (LXDE) with an RDP client is build. RDP servers addresses and options are simply passed from PXE server in boot parameters.
* You can change single parameter in config and the minimal console system will be built. It's a good basis for your own custom build.
* If boot failed because of server or network problem, it will briefly display an error message and start over. It's convenient that when problems are fixed, workstations will start themselves without manual interaction.

In the bank we used VNC to connect to user's thin client(it was `x11vnc` to connect to running Xorg session). This is not reuired for anyone(usually it is enough to connect to user's RDP session on a ternimal server), and conveniency/security requirements differ a lot for different environments. Therefore, I did not include that part.

## Alternatives

Why not just use [Thinstation](http://www.thinstation.org/)?

Well, if Thinstation completely statisfies your requirements - you better use it, it's more old and mature project. Plus it is about one and a half times smaller in size, because it is specially created for minimal size, not just slightly modified standard Ubuntu.

But it has ancient versions of software, and not a lot of it. If you need something special, not just client for RDP/Citrix/..., you would have to build it yourself, and do so for each update.

## Vagrant vs chroot

Previous versions used chroot, like most of similar projects do, Thinstation for example. It is easy, but program running in chroot is not exacltly the same as program running on real or virtual machine: there is no interction with system init, with other programs and services. And Vagrant made the build process as simple as possible: you just configure a virtual machine like you do for real one, and that's it.

Of course, using Vagrant brings some difficulties.

The `virtualbox-guest-utils` service should be running on the virtual machine, for shared folders to work. In addition, you need a boot manager(`grub`), mandatory for a machine with disk and useless for network boot client. I solved this problems by excluding this packages files from build, so they do not affect the size of resulting image.

Besides, Vagrant requires working ssh, that allows login for a user with Vagrant generated key. I exclude the vagrant user's home folder with that key. You can put ssh key for ubuntu user - that one is used for work - into it's home directory.

And Vagrant generates network interfaces configuration, that won't work on real machine. So I have to swap `interfaces` file during the build, and I created a script, that on real machine generates `interfaces` config with all available interfaces configured with DHCP.

Provisioning is done with Ansible. It is very convenient tool to configure all kinds of software and hardware. But I didn't want to include Ansible and python2 that is requires into the resulting image: useless waste of space. Installing Ansible on the real machine, that runs Vagrant and VirtualBox, is also a bad option: this will complicate the build process.

Vagrant allows you to make a trick: install Ansible on one virtual(test PXE server), and provision other virtuals from it. To do so, the virtuals should have static IP addresses. Well, we already solved the interfaces confiuration problem.

## The naughty squash

[Squashfs](https://en.wikipedia.org/wiki/SquashFS) is compressing red-only filesystem. It is used in most of existing Linux LiveCD. It allows you to create a fairly compact system image, located inside the RAM.

A lot of things should be cut of the resulting image:  `/tmp`, `/run`, `/proc`, `/sys`, `/usr/share/doc` and so on.

Utility `mksquashfs` supports as many as 3 types of lists to exclude files: by full path, by masks and by regular expresions. It would seem that everything is fine. But last two options do not support paths starting with `/`. I could not exclude files inside some directory without excluding the directory itself.

I got tired of fighting with it, so I just use `find` to fild all files and directories to exclude, and put it all into a single huge file with full paths. Ugly_crutch.jpg. But it works. The only artifact for this approach is the lonely directory `/proc/NNN`, corresponding to mksquashfs process idm which did not exist when the exclude list was created. procsfs is anyway mounted on top of it.

## Initrd magick

In order not to drag inside kernel all required drivers and an logic for mounting the root FS, Linux uses initial ramdisk. Previously, the initrd format was used, in which the disk was an actual filesystem image. A new format appeared in 2.6 kernel - initrams, which is cpio archive extracted to tmpfs. Both initrd and initrams can be compressed to save the loading time. A lot of tools and filenames still mention initrd, though it is not used anymore.

Debian/Ubuntu uses package initramfs-tools to create initramfs. It provides the following customization options:

* hooks - special format scripts, that allow you to add kernel modules and executable files with all required libraries.
* scripts inside directories `init-bottom`, `init-premount`, `init-top`, `local-block`, `local-bottom`, `local-premount`, `local-top`, executed in apropriate time on boot. See [man initramfs-tools(8)](http://manpages.ubuntu.com/manpages/xenial/en/man8/initramfs-tools.8.html).
* the most interesting option - you can add your own boot scripts, that mount the root FS. This scripts should define shell function `mountroot()`, which will be used by the main script `/init`. initramfs-tools already includes script `local` to mount root FS on local drive and `nfs` to mount root FS over network. Use script is selected by the boot parameter `boot`.

So, to mount the root FS in some tricky way, you have to create your own boot script, define function `mountroot()` in it, pass this script name in boot parameter `boot`. And don't forget to write hooks that will include into initramfs all required kernel modules and executables.

## Overlays

Для создния единой корневой файловой системы из нескольких используется [OverlayFS](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt). В первых версиях использовалась AUFS(она используется большинством линусковых LiveCD). Но её не приняли в ядро, и сейчас всем рекомендуют переходить на OverlayFS.

После монтирования настоящей корневой ФС в каталог внутри initramfs, будет запущена программа `run_init` из состава `klibc-utils`. Она проверит, что кореневая ФС смонтирована внутри initramfs, отчистит initramfs(зачем зря терять память?) и переместит точку монтирования корневой ФС в `/`. [Подробности](https://askubuntu.com/a/910374/25924). Эта программа собрана в виде отдельного исполняемого файла, потому что скрипт, использующий любые внешние утилиты, сломается после отчистки initramfs.

Если корневая ФС собирается из нескольких оверлеев, смонтированных внутри initramfs, при работе `run_init` эти точки монтрования пропадают, и она ломается. Эту проблему можно решить, переместив точки монтирования оверлеев **внутрь** корневой ФС, где они уже не пропадут. Рекурсия :) Делается так: `mount --move olddir newdir`.

Apparmor пришлось отключить: её профили рассчитаны на прямое монтирование корневой ФС с одного устройства. При использовании OverlayFS она видит, что `/sbin/dhclient` это на самом деле `/AURS/root/sbin/dhclient`, и профиль ломается. Единственный вариант её использовать - переписать все профили для всех приложений, и обновлять при необходимости.

## Where the write support is requierd

Под идее, Linux может спокойно работать, когда все ФС примонтированы read-only. Но многие программы рассчитывают на возможность записи на диск, приходится монтировать туда tmpfs:

* `/tmp`, `/var/tmp` - понятно, нужны очень многим
* `/var/log` - пишем логи
* `/run` - без него не запустятся почти все сервисы
* `/media` - монтированиие подключенных носителей
* `/var/lib/system` - используется многими программами из systemd, в частности `systemd-timesyncd`
* `/var/lib/dhclient` - сюда dhclient записывает информацию о leases
* `/etc/apparmor.d/cache` - если вы всё-таки поборете AppArmor, то ему надо будет писать файлы в `/etc`. ИМХО отвратительно, для таких вещей есть `/var`.

## Summary

Если вы хотите собрать загружаемую по сети и работающую только из памяти сборку Ubuntu - вот тут есть готовый удобный конструктор: [thinclient](https://github.com/selivan/thinclient). Если потребутеся помощь - пишите в ЛС, подскажу.


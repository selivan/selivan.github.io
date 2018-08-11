---
layout: post
title:  "GRUB 2: password protection for all but default menu entries"
tags: [grub,linux]
comments_by_disqus: true
---

**WARNING**: Playing with grub can make your system unbootable. Be careful.

Let's say you don't want to allow anybody to boot from other media on your device. Protecting a BIOS/EFI with password is easy. But also you have a GRUB bootloader, which can boot from arbitrary media, has command line and is basically a small OS.

On the other hand, you don't want to enter additional password every time you turn on your device. You can protect with password any actions in grub, except booting existing menu entries without changing them.

First, define users and passwords. Grub 1 allowed only plaintext passwords in configs, which is not a good idea. Grub 2 allows to use hashed passwords with salt (PBKDF2 is used, which is not Cthulhu worshipers chant, but [Password-Based Key Derivation Function](https://en.wikipedia.org/wiki/PBKDF2)).

```bash
grub-mkpasswd-pbkdf2

Enter password:
Reenter password:
PBKDF2 hash of your password is grub.pbkdf2.sha512.10000.3D3AF9CADA7E87C4CC938C3127426AD71FA9C8D42311A923C739BD91B0EFFEE4488B71505C5C306282D94F1AA84801D231CAF53D2667621D3D2D6ACC728F2F40.51225B857D268B024BC0696D8B7D04BB94A2E0C26D495324780CD84B5FB55BA4EF7A1BFF452E76052DAC5FA9B8AD92A74FB38BD873845F223167B4687F35EC0A
```

`/etc/grub.d/01_password`:

```bash
#!/bin/sh
set -e

cat << EOF
set superusers="grub"
# NOTE: no newline after 'password_pbkdf2 grub'
password_pbkdf2 grub grub.pbkdf2.sha512.10000.3D3AF9CADA7E87C4CC938C3127426AD71FA9C8D42311A923C739BD91B0EFFEE4488B71505C5C306282D94F1AA84801D231CAF53D2667621D3D2D6ACC728F2F40.51225B857D268B024BC0696D8B7D04BB94A2E0C26D495324780CD84B5FB55BA4EF7A1BFF452E76052DAC5FA9B8AD92A74FB38BD873845F223167B4687F35EC0A
EOF
```

```bash
chmod a+x /etc/grub.d/01_password
```

Btw, grub allows to have other users than superuser, that have access to only some of menu entries.

Now, you have to define default menu entries as `--unrestricted`, allowing to use them without password. Linux menu entries are defined in file `/etc/grub.d/10_linux`. Simpliest way to change all entries is to modify `CLASS` variable in the beginning of the file:

```bash
CLASS="--class gnu-linux --class gnu --class os --unrestricted"
```

Now to update actual `/boot/grub/grub.cfg` you should run `update-grub`(for Debian-based OS, like Ubuntu) or `grub-mkconfig -o <path to grub.cfg>` for others (thanks [the_gnarts](https://www.reddit.com/user/the_gnarts) who pointed out this difference).

Links:

* [Ubuntu wiki Grub2 Passwords](https://help.ubuntu.com/community/Grub2/Passwords)
* [GNU GRUB2 Manual](https://www.gnu.org/software/grub/manual/grub/grub.html)

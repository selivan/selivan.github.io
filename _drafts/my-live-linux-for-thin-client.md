---
layout: post
title:  "Ubuntu based thin client made with your own hands"
tags: [ubuntu,pxe,thinclient]
---

*This article in russian: [https://habrahabr.ru/](habrahabr.ru/)*

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

В банке для удалённого подключения к тонкому клиенту пользователя использовался VNC(`x11vnc` для подключения к уже запущенной сессии Xorg). Это далеко не всем требуется(обычно хватает возможности подключения к сеансу RDP на сервере терминалов), и тут всё очень индивидуально в плане требований удобства/безопасности. Поэтому эту часть я выкладывать не стал.

## Аналоги

Почему бы просто не пользоваться [Thinstation](http://www.thinstation.org/)?

Если Thinstation полностью устраивает - то лучше пользоваться им, это более старый и зрелый проект. Плюс он раза в полтора меньше по размеру, всё-таки это специально заточенная под минимальный объём сборка, а не слегка допиленная обычная Ubuntu.

Но версии софта в нём достаточно древние и его там мало. Если нужно что-то дополнительное, помимо клиентов RDP/Citrix/... - потребуется собирать это руками, и так при каждом обновлении.

## Vagrant vs chroot

Прошлые версии использовали chroot, как собственно и большинство похожих проектов, тот же Thinstation к примеру. Это несложно, но всё-таки запущеннная в chroot отдельная программа не соответствует происходящему на реальной машине: нету взаимодействия с системным init, с другими программами и службами. Плюс Vagrant позволил сделать процесс создения клиента максимально простым: виртуалка настраивается как обычная машина.

Конечно, использование Vagrant приносит и некоторые сложности.

На машине должна работать служба `virtualbox-guest-utils`, для работы общих папок. Кроме того, нужен менеджер загрузки(`grub`), обязательный для машины с диском и бесполезный для загружаемого по сети клиента. Эти проблемы я решил, исключая из сборки все файлы этих пакетов. Поэтому на размер получившегося образа они не влияют.

Кроме того, для Vagrant обязателен работающий на машине ssh, пускающий пользователя со сгенерированным ключом. Самый неприятный момент. Ключ из собранного образа я для безопасности исключаю. Если кто-то захочет заходить на тонкие клиенты по ssh, надо слегка поменять скрипт сборки, чтобы при сборке архива с домашним каталогом(собирается отдельно, потому что меняется чаще всего - не хочется каждый раз перегенерить весь образ ради пары строчек в каком-нибудь конфиге) туда включался нужный ключ.

Ну и для работы Vagrant генерирует настройки сетевых интерфейсов, которые будут ошибочными для реальной машины. Пришлось на время сборки подменять файл `interfaces`, и написать скрипт, который на реальной машине генерирует конфиг для настройки всех доступных интерйефсов по DHCP.

Provisioning делается с помощью Ansible. Это очень удобный инструмент для конфигурации всяческого софта и железа. Но включать в итоговый образ Ansible и требующийся ему второй python с нужными билиотеками не хотелось бы: бесплезный балласт. Ставить Ansible на машину, где запукается виртуальное окружение, тоже не хочется: это усложнит работу.

Vagrant позволяет сделать хитрость: поставить Ansible на одну машину(тестовый PXE сервер), и с неё делать разворачивание других машин, в рамках той же playbook. Для этого машины должны иметь статический IP, чтобы прописать его в ansible inventory. Ну а проблему с конфигурацией интерфейсов мы решили в прошлом пункте.

## Непослушный кабачок

[Squashfs](https://en.wikipedia.org/wiki/SquashFS) - сжимающия read-only файловая система. Лежит в основе большинства существующих Linux LiveCD. Именно она позволяет создать достаточно компактный образ системы, помещающийся в оперативную память тонкого клиента.

Из итогового образа надо много чего вырезать: `/tmp`, `/run`, `/proc`, `/sys`, `/usr/share/doc` и так далее.

Утилита `mksquashfs` поддерживает аж 3 типа списков для исключения файлов: по полному пути, по маскам и по регулярным выражениям. Казалось бы, всё прекрасно. Но последние два варианта не поддерживают пути, начинающиеся с `/`. У меня не получилось исключить все файлы внутри некотороый структуры папок, не исключая последнюю папку.

Мне быстро надоело с ней бороться, я просто нашёл `find`-ом все файлы и папки, которые надо исплючить, и запихнул в один большой файл с исключениями по полному пути. Костыли.jpg. Но работает. Единственным артефактом этого подхода в итоговом образе остаётся одинокая папка `/proc/NNN`, соответствующая номеру процесса mksquashfs, которого при создании списка исключений ещё не было. Сверху всё равно монтируется procfs.

## Магия initrd

Чтобы не тянуть в составе ядра все необходимые драйвера и логику монтирования корневой ФС, Linux использует initial ramdisk. Раньше использовался формат initrd, в котором этот диск представлял собой настоящий образ файловой системы. В ядре 2.6 появился новый формат - initramfs, представляющий собой извлекаемый в tmpfs cpio-архив. Как initrd, так и initramfs могут быть сжаты для экономии времени загрузки. Многие названия утилит и имена файлов по-прежнему упоминают initrd, хотя он уже не используется.

В Debian/Ubuntu для создания initramfs используется пакет initramfs-tools. Он даёт следующие возможности для кастомизации:

* хуки - скрипты специального формата, которые позволяют добавлять в образ исполняемые файлы со всеми требуемыми им библиотеками и модули ядра
* скрипты в каталогах `init-bottom`, `init-premount`, `init-top`, `local-block`, `local-bottom`, `local-premount`, `local-top`, выполняемые в соответствующий момент загрузки. См. [man initramfs-tools(8)](http://manpages.ubuntu.com/manpages/xenial/en/man8/initramfs-tools.8.html)
* самое интересное - добавлять собственные скрипты загрузки, отвечающие за монтирование корневой ФС. Они должны определять shell функцию `mountroot()`, которая будет использована главным скриптом `/init`. В составе уже есть `local` для монтирования корня на локальном диске и `nfs` для монтирования корня по сети. Используемый скрипт выбирается парамертом загрузки `boot`.

Итого, чтобы примонтировать корневую ФС каким-то сильно хитрым образом, надо создать свой скрипт загрузки, определить в нём функцию `mountroot()`, передать имя этого скрипта в параметре загрузки `boot` и не забыть написать хуки, подтягивающие в initramfs все нужные скрипту программы и модули ядра.

## Борьба за оверлеи

Для создния единой корневой файловой системы из нескольких используется [OverlayFS](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt). В первых версиях использовалась AUFS(она используется большинством линусковых LiveCD). Но её не приняли в ядро, и сейчас всем рекомендуют переходить на OverlayFS.

После монтирования настоящей корневой ФС в каталог внутри initramfs, будет запущена программа `run_init` из состава `klibc-utils`. Она проверит, что кореневая ФС смонтирована внутри initramfs, отчистит initramfs(зачем зря терять память?) и переместит точку монтирования корневой ФС в `/`. [Подробности](https://askubuntu.com/a/910374/25924). Эта программа собрана в виде отдельного исполняемого файла, потому что скрипт, использующий любые внешние утилиты, сломается после отчистки initramfs.

Если корневая ФС собирается из нескольких оверлеев, смонтированных внутри initramfs, при работе `run_init` эти точки монтрования пропадают, и она ломается. Эту проблему можно решить, переместив точки монтирования оверлеев **внутрь** корневой ФС, где они уже не пропадут. Рекурсия :) Делается так: `mount --move olddir newdir`.

Apparmor пришлось отключить: её профили рассчитаны на прямое монтирование корневой ФС с одного устройства. При использовании OverlayFS она видит, что `/sbin/dhclient` это на самом деле `/AURS/root/sbin/dhclient`, и профиль ломается. Единственный вариант её использовать - переписать все профили для всех приложений, и обновлять при необходимости.

## Где нужна возможность записи

Под идее, Linux может спокойно работать, когда все ФС примонтированы read-only. Но многие программы рассчитывают на возможность записи на диск, приходится монтировать туда tmpfs:

* `/tmp`, `/var/tmp` - понятно, нужны очень многим
* `/run` - без него не запустятся почти все сервисы
* `/var/lib/system` - используется многими программами из systemd, в частности `systemd-timesyncd`
* `/var/lib/dhclient` - сюда dhclient записывает информацию о leases
* `/etc/apparmor.d/cache` - если вы всё-таки поборете AppArmor, то ему надо будет писать файлы в `/etc`. ИМХО отвратительно, для таких вещей есть `/var`.

## Итого

Если вы хотите собрать загружаемую по сети и работающую только из памяти сборку Ubuntu - вот тут есть готовый удобный конструктор: [thinclient](https://github.com/selivan/thinclient). Если потребутеся помощь - пишите в ЛС, подскажу.


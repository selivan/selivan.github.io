---
layout: post
title:  "Building McAfee mysql audit plugin for Percona XtraDB Cluster 5.5 on Ubuntu 14.04.Trusty"
tags: [mysql,pxc,audit]
---
Percona XtraDB Cluster already includes audit plugin: [Percona Server 5.5 Audit Log Plugin](https://www.percona.com/doc/percona-server/5.5/management/audit_log_plugin.html). It is alternative implementation of MySQL Enterprise Audit Log Plugin by Oracle. Unfortunately, in 5.5 version it can not exclude some users from logging. For some use cases this faeture is crucial.

[McAfee mysql audit plugin](https://github.com/mcafee/mysql-audit) can do it for any mysql version: 5.5, 5.6, 5.7. There are no pre-compiled binaries for PXC 5.5, so we need to build it manualy, which is a little tricky.

Add Precona repository and install PXC packages, including packages with debug symbols:
```
wget https://repo.percona.com/apt/percona-release_0.1-3.$(lsb_release -sc)_all.deb
sudo dpkg -i percona-release_0.1-3.$(lsb_release -sc)_all.deb
sudo apt-get update
sudo apt-get install percona-xtradb-cluster-server-5.5 percona-xtradb-cluster-server-debug-5.5
```

Install packages required to build PXC:
```
sudo apt-get build-dep percona-xtradb-cluster-server-5.5
sudo apt-get install git gdb
```

To build mcafee-mysql-audit, we need automake-1.15. We can install it from [ondrej/autotools ppa](https://launchpad.net/~ondrej/+archive/ubuntu/autotools):
```
sudo add-apt-repository ppa:ondrej/autotools
sudo apt-get update
sudo apt-get install automake
```

Get PXC sources:
```
apt-get source percona-xtradb-cluster-server-5.5
```

Get mcafee mysql-audit source for latest stable version(( See most recent tag for https://github.com/mcafee/mysql-audit )):
```
git clone https://github.com/mcafee/mysql-audit.git
cd mysql-audit
git checkout v1.0.9
```

Configure and build PXC sources. Some headers there are present in *.h.in form, and we need to get pure *.h. Also for 5.5 version we need static library libmysqlservices.a:
```

```



######################################
http://askubuntu.com/questions/27677/cannot-find-install-sh-install-sh-or-shtool-in-ac-aux

libtoolize --force
aclocal
autoheader
automake --force-missing --add-missing
autoconf
./configure

http://stackoverflow.com/questions/33278928/how-to-overcome-aclocal-1-15-is-missing-on-your-system-warning-when-compilin

Before running ./configure try running autoreconf -f -i. The autoreconf program automatically runs autoheader, aclocal, automake, autopoint and libtoolize as required.

--------------------------------------------------------------------------------------------------------------------

make -f debian/rules configure

-- Configuring done
-- Generating done
-- Build files have been written to: /root/percona-xtradb-cluster-5.5-5.5.41-25.11/builddir

make -f debian/rules build

copy /root/percona-xtradb-cluster-5.5-5.5.41-25.11/builddir to /root/percona-xtradb-cluster-5.5-5.5.41-25.11 , no overwrite

./configure --with-mysql=/root/percona-xtradb-cluster-5.5-5.5.41-25.11 --with-mysql-libservices=/root/percona-xtradb-cluster-5.5-5.5.41-25.11/libservices/libmysqlservices.a

make

Result: ./src/.libs/libaudit_plugin.so

New autotools: https://launchpad.net/~ondrej/+archive/ubuntu/autotools


Extract offset:

apt-get install gdb
https://github.com/mcafee/mysql-audit/wiki/Troubleshooting#offset-extraction

./offset-extract.sh /usr/sbin/mysqld /usr/sbin/mysqld-debug

//offsets for: /usr/sbin/mysqld (5.5.41-37.0-55)
{"5.5.41-37.0-55","4aa67e7bbbde1b77a557fcbb7df995dc", 6640, 6688, 4168, 4688, 104, 2608, 96, 0, 32, 104, 136, 6792},

my.cnf:

plugin-load=AUDIT=libaudit_plugin.so
audit_validate_checksum=OFF
audit_checksum=4aa67e7bbbde1b77a557fcbb7df995dc
audit_offsets=6640, 6688, 4168, 4688, 104, 2608, 96, 0, 32, 104, 136, 6792

Latest offset extraction script: https://raw.githubusercontent.com/mcafee/mysql-audit/master/offset-extract/offset-extract.sh


https://github.com/mcafee/mysql-audit/issues/69



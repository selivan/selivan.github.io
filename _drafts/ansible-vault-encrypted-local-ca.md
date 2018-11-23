---
layout: post
title:  "Encrypted local PKI CA for SSL/TLS keys and certificates with ansible vault"
tags: [ansible,ansible-vault,openssl,easy-rsa]
---

Sometimes you may need a local PKI CA, for example to use it with an OpenVPN server or to secure HTTPS traffic between your hosts in private network. Easiest and popular way to do it is [easy-rsa](https://github.com/OpenVPN/easy-rsa).

It keeps ca and client keys in unencrypted files, and it reqires this files to manage the PKI. If you want to keep this PKI files in your Ansible repository in a secure way, encrypted with ansible-vault, you have to do a lot of manual work. 

Simpliest way would be to keep plain PKI directory somewhere near Ansible repository, manage files there and copy and encrypt changed files with ansible-vault. A lot of extra work and not very secure.

I nailed together a couple of scripts that allow you to keep the keys encrypted inside Ansible repository. They are decrypted with ansible-vault only for a short time to manage the PKI, then encrypted back.

Usage:


`new-cadir.sh roles/vpnserver/files/ca` - creates new ca in given directory:

```
roles/vpnserver/files/ca/vars
roles/vpnserver/files/ca/openssl-1.0.0.cnf
roles/vpnserver/files/ca/keys/ca.crt
roles/vpnserver/files/ca/keys/ca.key <- ENCRYPTED
roles/vpnserver/files/ca/keys/dh2048.pem <- ENCRYPTED
roles/vpnserver/files/ca/keys/...
```


`new-cert.sh roles/vpnserver/files/ca client|server name` - creates this files:

```
roles/vpnserver/files/ca/keys/name.crt
roles/vpnserver/files/ca/keys/name.csr
roles/vpnserver/files/ca/keys/name.key <- ENCRYPTED
```

Second argument specifies the certificate type: client or server.

Directory `roles/vpnserver/files/ca.plaintext` containing unencrypted files is created while the script works and deleted when it finishes. Good practice is to add this directory to `.gitignore`/`.hgignore` file, in case the script is interrupted, to avoid accidential adding unencrypted files to version control.

Scripts require `openssl` and `make-cadir`(from easy-rsa) to be available in `$PATH`.

The scripts:

[new-cadir.sh](https://gist.github.com/...)

[new-cert.sh](https://gist.github.com/...)

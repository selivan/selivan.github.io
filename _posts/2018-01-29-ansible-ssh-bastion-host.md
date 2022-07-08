---
layout: post
title:  "Using Ansible with bastion host"
tags: [ansible,ssh,bastion]
comments_by_utterance: true
---

**UPD** Another article on the this topic, using variables instead of ssh config file: [Using Ansible with bastion or jump host with variables](/2020/10/30/ansible-ssh-bastion-host-with-variables.html).

Sometimes due to network configuration or security reasons you can't access a host directly, but should use intermediate host, so-called bastion host.

I got this setup from [this article by Scott Lowe](https://blog.scottlowe.org/2015/12/24/running-ansible-through-ssh-bastion-host/), but `ssh.cfg` is adjusted so that mentioning exact network mask is not necessary.

`ansible.cfg`:

```ini
[ssh_connection]
# -C enable compression
ssh_args = -C -F ./ssh.cfg
```

`ssh.cfg`:

```bash
# All hosts
Host *
# Security
ForwardAgent no
# Connection multiplexing
ControlMaster auto
ControlPersist 2m
ControlPath ~/.ssh/ansible-%r@%h:%p
# Connect through bastion hosts
ProxyCommand ssh -W %h:%p bastion1
# Second bastion if first is down
#ProxyCommand ssh -W %h:%p bastion2

# Bastion hosts
Host bastion1
HostName 10.0.0.1
ProxyCommand none

Host bastion2
HostName 10.0.0.2
ProxyCommand none
```

Somewhere in inventory, to avoid repeating bastion IP addresses twice:

```ini
[bastion]
bastion1 ansible_ssh_host=bastion1
bastion2 ansible_ssh_host=bastion2
```

**P.S.** Starting from Ansible 2, you can also use `ProxyCommand` in `ansible_ssh_common_args` inventory variable: [Ansible FAQ](https://docs.ansible.com/ansible/latest/faq.html#how-do-i-configure-a-jump-host-to-access-servers-that-i-have-no-direct-access-to).

**UPD**: [stemid85](https://www.reddit.com/user/stemid85) on Reddit [pointed out](https://www.reddit.com/r/linuxadmin/comments/7tp0q1/using_ansible_with_bastion_host/dtfp057/) the way to use a chain of bation hosts:

```
Host bastion1
  HostName 192.168.1.1
  ProxyCommand none

Host bastion2
  HostName 192.168.2.2
  ProxyCommand ssh bastion1 -W %h:%p                                                                                         

Host target
  ProxyCommand ssh bastion2 -W %h:%p                                                                                         
```

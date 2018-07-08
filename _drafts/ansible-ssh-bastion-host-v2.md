---
layout: post
title:  "Using Ansible with bastion host version 2: multiple environments, different bastion hosts"
tags: [ansible,ssh,bastion,jump_host]
---
Some time ago I made an article [post](/2018/01/29/ansible-ssh-bastion-host.html) on using ansible with bastion host. It works fine, but the approach is a bit clumsy: you need to create ssh.cfg files; if you want to have host IP in ansible_hostm then IP addresses are duplicated between file and inventory; if you use multiple environments(for example: prod, stage and dev1-dev5), you need separate ssh.cfg file for each one; using different bastion hosts for different host groups is painful. Clumsy.

You may need multiple bastion hosts if you have multiple datacenters, or if you are using LXD contianers without exposing their SSH ports outside.

Here is my second approach on this task.

`inventory_file`:


```ini
{% raw %}
[all:vars]
# HERE GOES MAGIC
# To change used bastion host for host or group, set variable bastion_host
# To disable using bastion host(at least on bastion hosts themself), set bastion_host=''
# Also disables strict hostkeyy check for hosts behind bastion
# See https://docs.ansible.com/ansible/2.6/plugins/connection/ssh.html
ansible_ssh_common_args="{% if bastion_host is defined and bastion_host | length != 0 %} -o 'ProxyCommand ssh -W %h:%p {{ hostvars[bastion_host].ansible_host }} {% if hostvars[bastion_host].ansible_user is defined %} -o User={{ hostvars[bastion_host].ansible_user }}{% endif %} {% if hostvars[bastion_host].ansible_port is defined %} -o Port={{ hostvars[bastion_host].ansible_port }}{% endif %} -o ControlMaster=auto -o ControlPersist=5m ' -o StrictHostKeyChecking=no {% endif %}"

# Default bastion host. If not set, will not be used unless explcitly specified
bastion_host=bastion1

[bastion]
bastion1 ansible_host=10.0.0.1
bastion2 ansible_host=10.0.0.2
[bastion:vars]
bastion_host=''

[hosts_accessable_via_default_bastion]
srv1 ansible_host=192.168.0.1
srv2 ansible_host=192.168.0.2

[hosts_accessable_via_other_bastion]
srv3 ansible_host=172.16.0.3
srv4 ansible_host=172.16.0.4
[hosts_accessable_via_other_bastion:vars]
bastion_host=bastion2

[hosts_accessable_directly]
srv5 ansible_host=172.31.0.5
srv6 ansible_host=172.31.0.6
[hosts_accessable_directly:vars]
bastion_host=''
{% endraw %}
```

*Downside*: this solution does not support chained bastion hosts. (? make it support them?)

How it works.


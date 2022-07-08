---
layout: post
title:  "Using Ansible with bastion or jump host with variables"
tags: [ansible,ssh,bastion]
comments_by_utterance: true
---

Sometimes due to network configuration or security reasons you can't access a host directly, but should use intermediate host, so-called bastion or jump host.

My presious article on this topic, using ssh config file: [Using Ansible with bastion host](/2018/01/29/ansible-ssh-bastion-host.html).

Another option is using variables. This approach is more flexible: it is easier to define different bastion hosts for different hosts and groups with variables.

Simplest option is to directly mention bastion host address and user:

`group_vars/all/ansible_ssh.yml`:

```yaml
ansible_ssh_common_args: "-o ProxyCommand=\"ssh <bastion user>@<bastion address> -o Port=<bastion ssh port> -W %h:%p\""
```

And of course don't forget to reset that variable for the bastion host itself:

`host_vars/bastion_host/ansible_ssh.yml`:

```yaml
ansible_ssh_common_args: ""
```

Downside of simple option is duplicating bastion host coordinates in variables and in inventory. More complex setup to avoid the duplication:

`group_vars/all/ansible_ssh.yml`:

{% raw %}
```yaml
ansible_ssh_proxy_command: >-
  {% if bastion_host is defined and bastion_host != '' %}
  ssh {{ hostvars[bastion_host]['ansible_ssh_user'] }}@{{ hostvars[bastion_host]['ansible_ssh_host'] }}
  -o Port={{ hostvars[bastion_host]['ansible_ssh_port'] | default(22) }}
  -W %h:%p
  {% endif %}

ansible_ssh_common_args: >-
  {% if bastion_host is defined and bastion_host != '' %}
  -o ProxyCommand="{{ ansible_ssh_proxy_command }}"
  {% endif %}

# Default bastion host for all hosts
bastion_host=bastion1

```
{% endraw %}

And you still have to mention that bastion host itself doesn't need this:

`host_vars/bastion_host/ansible_ssh.yml`:

```yaml
bastion_host: ""
```

---
layout: post
title:  "Ansible: multi-line shell script inside playbook"
tags: [ansible, bash]
---
Sometimes ansible is not enough, and you want to unleash the raw shell power. But long one-line scripts look totally unreadable. Here is how you can do it with YAML multi-line representation:

```yaml
- name: long shell script
  shell: |
    cat /proc/cmdline | tr ' ' '\n' | while read param; do
        if [[ "$param" == root=* ]]; then
            echo ${param#root=}
        fi
    done
  args:
    executable: /bin/bash
  register: boot_param_root
```

Links:
* [stackoverflow.com - In YAML, how do I break a string over multiple lines?](https://stackoverflow.com/a/21699210/890863)

**UPD** [https://www.reddit.com/user/androidul](https://www.reddit.com/user/androidul) on reddit suggested to use [file or template lookups](http://docs.ansible.com/ansible/latest/playbooks_lookups.html#more-lookups) for embedding long scripts. IMHO that's a good idea for really large scripts, but for 5-7 lines YAML multiline is more readable.

```yaml
- name: large shell script
  shell: shell: "{{ lookup('template', 'large_script.j2') }}"
  args:
    executable: /bin/bash
  register: large_script_result
```

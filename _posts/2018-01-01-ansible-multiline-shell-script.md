---
layout: post
title:  "Ansible: multiline shell script inside playbook"
tags: [ansible, bash]
---
Sometimes ansible is not enough, and you want to unleash the raw shell power. But long one-line scripts look totally unreadable. Here is how you can do this with YAML multi-line representation:

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

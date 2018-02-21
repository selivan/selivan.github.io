---
layout: post
title:  "Ansible running multiple handlers subtelty"
tags: ansible
---

In ansible, to run multiple handlers for a task you can chain handlers by `notify` dependencies, like in [this stackoverflow answer](http://stackoverflow.com/a/31618968/890863). There is a small subtelty here. Notify action is triggered only if task was changed. Some tasks do not change at all(like `debug: msg=...`), some tasks do not always change. To run all required handlers surely you should set `changed_when: True` for all of them except the last one:

```yaml
handlers:
  # At first check if nginx config is correct
  - name: restart nginx
    shell: nginx -t
    changed_when: True
    notify: restart nginx step 2

  - name: restart nginx step 2
    service: name=nginx state=restarted
```

**UPD**: Since Ansible 2.3, [named block](http://docs.ansible.com/ansible/latest/playbooks_blocks.html) could be more elegant solution. Unfortunately, blocks do not work in handlers: [ansible #36480](https://github.com/ansible/ansible/issues/36480).

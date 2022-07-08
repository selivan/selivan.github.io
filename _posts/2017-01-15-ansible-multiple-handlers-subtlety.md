---
layout: post
title:  "Ansible running multiple handlers subtelty"
tags: ansible
comments_by_utterance: true
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

**UPD2**: Task may have multiple handlers like this:

```yaml
- template: src=foo.j2 dest=/etc/foo
  notify:
    - restart foo
    - restart bar
```

But **be careful**: handlers will always run in order they are defined, not in order they are listed in `notify:`

**UPD3**: Since Ansible 2.2, handlers can "listen" to some topic:

```yaml
handlers:
    - name: restart memcached
      service: name=memcached state=restarted
      listen: "restart web services"
    - name: restart apache
      service: name=apache state=restarted
      listen: "restart web services"
tasks:
    - command: echo "this task will restart the web services"
      notify: "restart web services"
```

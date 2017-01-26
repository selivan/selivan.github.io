---
layout: post
title:  "ansible multiple handlers subtelty"
tags: ansible
---

In ansible, to run multiple handlers for a task you can chain handlers by `notify` dependencies, like in [this stackoverflow answer](http://stackoverflow.com/a/31618968/890863). There is a small subtelty here. Notify action is triggered only if task was changed. Some task do not change at all(like `debug: msg=...`), some tasks change not always. To run all required handlers surely you should set `changed_when: True` for all except the last one:

```yml
- name: start apt mirroring
  debug: msg="check logs in /var/log/apt-mirror-cron.log"
  changed_when: True
  notify: start apt mirroring step 2

- name: start apt mirroring step 2
  shell: sudo -u apt-mirror /usr/bin/apt-mirror >> /var/log/apt-mirror-cron.log
  async: 6000
  poll: 0

```

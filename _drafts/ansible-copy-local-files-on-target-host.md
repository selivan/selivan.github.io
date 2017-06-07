---
layout: post
title:  "Ansible: copy local files on target host"
tags: [ansible,rsync]
---
Ansible dosn't have convenient way to copy files within target host. At least, I didn't find any. Directly using `cp` command is not the best option. Files will be copied every time and task will always be marked as changed. Other downside is that check mode won't work for `command` and `shell` modules.

To make this right, you can use `rsync` command on target host with some hacks:

```yaml
- set_fact:
    rsync_dry_run: "--dry-run"
  when: ansible_check_mode

- name: copy files within target host
  shell: rsync "{{ rsync_dry_run }}" --itemize-changes --archive /src/dir/ /dest/dir/
  check_mode: yes
  register: rsync_result
  changed_when: rsync_result.stdout != ''
```

Check mode will show, whether the task is to change files, and files won't be copied if they already are in place.

`--itemize-changes` makes `rsync` output a change-summary for every updated file.

Other options thay you may want to use with `rsync` in this task:
  * `--update` skip files that are never in destination
  * `--checksum` do not skip files based on mod-time and size, use checksum

Yep, ansible will brag about using [synchronize module](http://docs.ansible.com/synchronize_module.html) instead of rsync, but it can not work within destination host.

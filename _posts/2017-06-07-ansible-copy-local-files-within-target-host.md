---
layout: post
title:  "Ansible: properly copy local files within the target host"
tags: [ansible,rsync]
comments_by_disqus: true
---

**UPD**: reddit user [FireReadyAim](https://www.reddit.com/user/FireReadyAim) [pointed out](https://www.reddit.com/r/ansible/comments/6fvryi/ansible_properly_copy_local_files_within_the/dilj19l/), that copy module supports `remote_src` parameter. It was added in ansible 2.0, I've missed it. It works with directories too. But it does not support copying owners, permissions, acls and xattrs, so my solution is still useful in some cases.

---

Ansible doesn't have a convenient way to copy files within target host. Directly using `cp` command is not the best option. Files will be copied every time and task will always be marked as changed. Other downside is that check mode won't work for `command` and `shell` modules.

To make this properly, you can use `rsync` command on target host with some hacks:

```c
{% raw %}
- set_fact:
    rsync_dry_run: "--dry-run"
  when: ansible_check_mode

- name: copy files within target host
  shell: rsync --itemize-changes --archive --acls --xattrs {{ rsync_dry_run | default('') }} /src/directory/ /dest/directory/
  # always run
  check_mode: no
  register: rsync_result
  changed_when: rsync_result.stdout != ''
{% endraw %}
```

Check mode will show, whether the task is to change files, and files won't be copied if they already are in place.

`--itemize-changes` makes `rsync` output a change-summary for every updated file.

Other options thay you may want to use with `rsync` in this task:

* `--update` skip files that are never in destination
* `--ignore-existing` do not update files that exist in destination
* `--checksum` do not skip files based on mod-time and size, use checksum

Yep, ansible will brag about using [synchronize module](http://docs.ansible.com/synchronize_module.html) instead of rsync, but it can not work within destination host.

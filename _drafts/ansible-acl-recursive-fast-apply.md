---
layout: post
title:  "Ansible recursive ACLs: workaround for fast apply"
tags: [ansible, acl]
---
If you are setting acls recursive for directory with a lot of files, playbook is applying very slow, bacause it checks acl for each file. If you use default acls, then every newly created file will get right acl. So only time when you realy want recursive work is when you are applying playbook first time. Here is a workround to do so:
```yaml
- name: set acls
  acl: path=/some/path state=present etype=user entity=www-data permissions="rX" recursive=no
  register: dirs_acls_updated

# Output of this task is realy huge, so it's suppressed
- name: set directory acls for user www-data in {{ webapp_dir }} with recursion
  acl: path=/some/path state=present etype=user entity=www-data permissions="rX recursive=yes
  when: app_dirs_acls is defined and app_dirs_acls.changed
  no_log: True
```

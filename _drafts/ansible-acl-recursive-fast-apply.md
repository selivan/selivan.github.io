---
layout: post
title:  "Ansible recursive ACLs: workaround for fast apply"
categories: [ansible, acl]
---
If you are setting acls recursive for directory with a lot of files, playbook is applying very slow, baceuse it checks acl for each file. If you use default acls, then every newly created file will get right acl. So only time when you realy want recursive work is when you are applying playbook first time.
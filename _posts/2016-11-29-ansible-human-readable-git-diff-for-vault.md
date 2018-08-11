---
layout: post
title:  "Ansible: human readable git diff for vault encrypted files"
tags: [ansible,git]
comments_by_disqus: true
---

Ansible vault can be used transparently with `copy` module and variable files: `include_vars`, `vars_files`. IMHO that's bad architecture. "Explicit is better than implicit" (c) Python Zen. In our project we agreed to keep vault encrypted files with extension `.vault` and vault encrypted variable files with `.vault.yml`.

To make git diffs human-readable, we can use [git attributes](https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes) to specify properties for different pathnames in git repository.

`.gitattributes`:

```git
*.vault diff=ansible-vault merge=binary
*.vault.yml diff=ansible-vault merge=binary
```

Attribute `diff` controls how git generates diffs for this files. `merge` controls how 3 versions of file are merged. `binary` is built-in merge driver, that keeps file version from working tree, but leaves the path in conflicted state. We don't want ansible vault files to be merged automatically :) And we just have to configure specified diff driver:

```shell
git config diff.ansible-vault.textconv 'PAGER=cat ansible-vault view'
git config diff.ansible-vault.cachetextconv false
```

This will also make `git blame` work fine for this files, but only if they always were encrypted during repository history.

I found this idea here: [github.com/building5/ansible-vault-tools](https://github.com/building5/ansible-vault-tools). It also has scripts to make human-readable merge possible for vault encrypted files, but that requires little more complex setup.

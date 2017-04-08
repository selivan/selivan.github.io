---
layout: post
title:  "Ansible check before commit that all *.vault files are encrypted"
tags: [ansible,ansible-vault,git]
---

In our project we have an agreement: all vault-encrypted files should have suffix `.vault`. It's convenient to be able to see that all secret information, like keys and passwords, is stored properly.

But this system has one drawback: it's easy to rename file to `*.vault` but forget to actually encrypt it.

Our ansible playbooks are stored in git repository, so we can use [git hooks](https://git-scm.com/docs/githooks) to force our rules. We will use `pre-commit` hook, that is executed by `git commit`, and it's non-zero exit status aborts the commit.

We want to check only changed files. `git diff` command with `--cached` option shows only changes added to git index for commit.

Handling pathnames with spaces and/or special characters is tricky in shell. `git diff` has `-z` option to use NULL characters as pathname terminators. Built-in bash command `read` has `-d` option to specify the last line character and `-r` to disable interpretation of backslash escaped characters(like `'\t'`). It uses characters from `$IFS` variable(default `$' \t\n'`) as word delimiters. If we set `$IFS` empty, whole line before NULL will be saved to a variable.

If we redirect some command output to a loop(`while` or `for`), that loop will be running in separate subshell. Variables changed inside loop won't be visible to parent shell, and `exit` command will terminate just the subshell, not the main script. To communicate with loop subshell we can use it's exit code.

`./git/hooks/pre-commit`:

```bash
#!/bin/bash

if git rev-parse --verify HEAD >/dev/null 2>&1
then
        against=HEAD
else
        # Initial commit: diff against an empty tree object
        against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Redirect output to stderr.
exec 1>&2

# Check that all changed *.vault files are encrypted
IFS=$'\n'
git diff --cached --name-only -z "$against" | IFS= while read -r -d $'\0' file; do
        [[ "$file" != *.vault && "$file" != *.vault.yml ]] && continue
        head -1 "$file" | grep --quiet '^\$ANSIBLE_VAULT;' || {
                echo "ERROR: non-encrypted *.vault file: $file"
                exit 1
        }
done
# while loop creates separate subshell, we can not use it's variables
exit $?
```

By default git hooks are located in `.git/hooks` directory outside version control. Of course we want to store hooks in repository to share them between all users. Let's save them to `git_hooks` directory in the repository root. Starting from version 2.9, git has config parameter `core.hooksPath`, that allows to set relative path for hooks:

```bash
git config core.hooksPath ./git_hooks
```

If we use an older version, we can use a simple script to create apropriate symlinks in `.git/hooks` to scripts in `git_hooks`. Here is one, it should be placed in `git_hooks` as well:

```bash
#!/bin/bash
# man githooks

git_hooks_dir=$(git rev-parse --show-toplevel)/.git/hooks
scripts_dir=$(dirname "$(readlink -f "$0")")
self_name=$(basename "$(readlink -f "$0")")

for hook in "$scripts_dir"/*; do
        hook_name=$(basename "$(readlink -f "$hook")")
        if [[ "$hook_name" != "$self_name" ]]; then
                ln --verbose --symbolic --force "$hook" "$git_hooks_dir/$hook_name"
        fi
done
```

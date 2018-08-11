---
layout: post
title:  "Ansible: check before commit that all *.vault files are encrypted"
tags: [ansible,ansible-vault,git]
comments_by_disqus: true
---

In our project we have an agreement: all vault-encrypted files should have suffix `.vault`. It's convenient to be able to see that all secret information, like keys and passwords, is stored properly.

But this system has one drawback: it's easy to rename a file to `*.vault` but forget to actually encrypt it.

Our ansible playbooks are stored in git repository, so we can use [git hooks](https://git-scm.com/docs/githooks) to force our rules. We will use `pre-commit` hook, that is executed by `git commit`. It's non-zero exit status aborts the commit.

Check if file is encrypted with ansible-vault is simple, first line of such file starts with `$ANSIBLE_VAULT;`

`./git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
#
# Called by "git commit" with no arguments.  The hook should
# exit with non-zero status after issuing an appropriate message if
# it wants to stop the commit.

# Unset variables produce errors
set -u

if git rev-parse --verify HEAD >/dev/null 2>&1
then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Redirect output to stderr.
exec 1>&2

EXIT_STATUS=0

# Check that all changed *.vault files are encrypted
# read: -r do not allow backslashes to escape characters; -d delimiter
while IFS= read -r -d $'\0' file; do
	[[ "$file" != *.vault && "$file" != *.vault.yml ]] && continue
	# cut gets symbols 1-2
	file_status=$(git status --porcelain -- "$file" 2>&1 | cut -c1-2)
	file_status_index=${file_status:0:1}
	file_status_worktree=${file_status:1:1}
	[[ "$file_status_worktree" != ' ' ]] && {
		echo "ERROR: *.vault file is modified in worktree but not added to the index: $file"
		echo "Can not check if it is properly encrypted. Use git add or git stash to fix this."
		EXIT_STATUS=1
	}
	# check is neither required nor possible for deleted files
	[[ "$file_status_index" = 'D' ]] && continue
	head -1 "$file" | grep --quiet '^\$ANSIBLE_VAULT;' || {
		echo "ERROR: non-encrypted *.vault file: $file"
		EXIT_STATUS=1
	}
done < <(git diff --cached --name-only -z "$against")

exit $EXIT_STATUS
```

Thank you [Ben Tennant](https://disqus.com/by/ben_tennant/) and [Flexic](https://disqus.com/by/flexic/) for helping to fix and improve this script.

We want to check only changed files. `git diff` command with `--cached` option shows only changes added to git index for commit.

If file was modified after `git add`, we can not check it's version that is going to be commited. So we ask user to fix the situation. We could use some automation here, like `git stash` before commit and `git stash pop` after, but I think leaving solution to user himself is better option.

Handling pathnames with spaces and/or special characters is tricky in shell. `git diff` has `-z` option to use NULL characters as pathname terminators. Built-in bash command `read` has `-d` option to specify the last line character and `-r` to disable interpretation of backslash escaped characters(like `'\t'`). It uses characters from `$IFS` variable(default `$' \t\n'`) as word delimiters. If we set `$IFS` empty, whole line before NULL will be saved to a variable.

If we use pipe to redirect some command output to `while` loop, it will be running in separate subshell. Variables changed inside loop won't be visible to parent shell, and `exit` command will terminate just the subshell, not the main script. To communicate with loop subshell we can use it's exit code.

By default git hooks are located in `.git/hooks` directory that is not under version control. Of course we want to store hooks in repository to share them between all users. Let's save them to `git_hooks` directory in the repository root. Starting from version 2.9, git has config parameter `core.hooksPath`, that allows to set relative path for hooks:

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

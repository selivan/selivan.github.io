---
layout: post
title:  "Job scripts in gitlab-runner with allocated pseudo-terminal tty"
tags: [gitlab,ci]
---

Some programs require terminal to work correctly. Btw, `ssh -t ...` that runs commands on remote host with allocated pseudo-terminal doesn't work if it is not launched from a shell attached to a terminal.

Gitlab-runner does not provide any options to do that, it runs all scripts in a job without tty.

The only workaround(quite ugly) I could find is using `script`:

```
build:
  scripts:
    - script --return --quiet -c "command" /dev/null
```

Thanks to [this](https://stackoverflow.com/a/1402389/890863) stackoverflow answer.

Feature request to add option to allocate tty to gitlab-runner: [#25467](https://gitlab.com/gitlab-org/gitlab-runner/-/issues/25467).

May be also helpful: https://docs.python.org/3/library/pty.html

---
layout: post
title:  "PCI DSS requirement for session idle timeout: implementation and bypass"
tags: [pcidss,bash]
comments_by_disqus: true
---
PCI DSS 3.2 requirement 8.1.8 states "If a session has been idle for more than 15 minutes, require the user to re-authenticate to re-activate the terminal or session".

For bash this may be achieved with this config:

`/etc/profile.d/set_tmout.sh`:

```bash
# Exit bash after 15 minutes of inactivity
TMOUT=900
export TMOUT
readonly TMOUT
```

For ssh sessions you should use this settings in `sshd_config`:

```
ClientAliveInterval 300
ClientAliveCountMax 3
```

Your auditor will be quite happy with this.

---

Problem is, if you like to open a lot of sessions in tmux/screen - with appropriate directory and commands history for particular task - this thing fucks up all your well-suited workflow.

You can not just unset `TMOUT` variable, because it is read-only. But happily, you can replace shell with another program by `exec` command. Pure `sh` respects the `TMOUT` setting, but it's simple and doesn't know a thing about read-only variables. So here is what you do:

```bash
alias fuckoff='exec sh -c "unset TMOUT; exec bash"'
```

Or even insert this in `.bashrc_local`(included from `.bashrc` and removed before audit):

```bash
test -n "$TMOUT" && exec sh -c "unset TMOUT; exec bash"
```

Voila! You have usable working environment again.

Of course, all this is purely theoretical. Nobody should ever bypass PCI DSS requirements with sneaky tricks. That's the law -_-

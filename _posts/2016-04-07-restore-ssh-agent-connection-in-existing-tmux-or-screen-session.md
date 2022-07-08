---
layout: post
title:  "Restore SSH Agent connection when attaching to existing tmux or screen session"
tags: [ssh,tmux,screen]
comments_by_utterance: true
---
When you use ssh agent, tmux or screen session gets it from environment variable `SSH_AUTH_SOCK`. Variable keeps path to socket, that was created for this connection. You close connection and create new one, then you attach to saved session. Now ssh to other servers from shells in this session won't work, because it has old `SSH_AUTH_SOCK` value. Here is workaround to fix it:

`.bashrc`:

```bash
if [ -n "$SSH_AUTH_SOCK" -a "$SSH_AUTH_SOCK" != "$HOME/.ssh/auth_sock" ]; then
		ln -sf $SSH_AUTH_SOCK $HOME/.ssh/auth_sock \
		&& export SSH_AUTH_SOCK=$HOME/.ssh/auth_sock
fi
```

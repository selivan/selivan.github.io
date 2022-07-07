---
layout: post
title:  "Simple bash debugger using trap DEBUG"
tags: [ bash ]
comments_by_utterance: true
---

Inspired by [this post](https://habr.com/ru/post/666982/) by [ @tminnigaliev](https://habr.com/ru/users/tminnigaliev/).

Besides traps(handlers) for signals, bash have 4 special traps:

* `EXIT` to run on exit from the shell.
* `RETURN` to run each time a function or a sources script finishes.
* `ERR` to run each time command failure would cause the shell to exit if `set -e` is used.
* `DEBUG` to execute before every command.

 The last one allows to create a simple debugger inside a bash script:

```bash
function _trap_DEBUG() {
    echo "# $BASH_COMMAND";
    while read -r -e -p "debug> " _command; do
        if [ -n "$_command" ]; then
            eval "$_command";
        else
            break;
        fi;
    done
}

trap '_trap_DEBUG' DEBUG
```

Now before executing every command, it is printed and we have a command prompt. There we can print any command to execute in the script context or an empty line to continue.

Also it is possible to run another script in this debugging mode without modifying it. The only catch is that bash functions and scripts inlined by `source` do not inherit DEBUG, RETURN and ERR traps. We can use `set -T` to allow inheriting DEBUG and RETURN traps.

Here is such a simple debugger with some bells and whistles added: [selivan/bash-debug](https://github.com/selivan/bash-debug)

Also it is worth mentioning that a gdb-like debugger for bash scripts exists: [bashdb](http://bashdb.sourceforge.net/). It has way more functionality but requires building from source and installation.

---
layout: post
title:  "Execute script before starting service in docker-compose"
tags: [ docker, docker-compose ]
comments_by_utterance: true
---

Sometimes you need to execute shell commands before starting service in docker compose.

You can create oneshot service using the image you need for those commands, entrypoint `/bin/sh` and shell commands in `command` option.

YAML multi-line syntax allows to conviniently place the script inside `docker-compose.yml`. Use `set -x` to get verbose logs of script execution. Don't forget that the last command should have exit code 0.

Then you make the main service dependent on oneshot service, with option `condition: service_completed_successfully`. Unlike default dependency, this one requires service to successfully finish execution, not to be runnig. Other possible conditions are `service_started`(default) and `service_healthy`(healthcheck ok).

`docker-compose.yml`:
```yaml
services:
  create-mysql-socket-dir:
    image: "busybox:stable"
    restart: "no"
    entrypoint: /bin/sh
    command:
    - "-c"
    - |
      set -x
      mkdir -p /var/run/mysqld
      chown ${MYSQL_UID}:${MYSQL_GID} /var/run/mysqld
    volumes:
      - /var/run:/var/run
  mysql:
    image: percona/percona-server:5.7
    depends_on:
      create-mysql-socket-dir:
        condition: service_completed_successfully
    user: "${MYSQL_UID}:${MYSQL_GID}"
    volumes:
      - /var/run/mysqld/:/var/run/mysqld/
    command: "--socket=/var/run/mysqld/mysqld.sock"
  ...
```

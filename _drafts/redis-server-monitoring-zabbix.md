TODO: generalize, like:

```
# Arguments: section, parameter
# Examples:
# replication, role
# memory, used_memory
# replication, repl_backlog_size
# replication, repl_backlog_active
UserParameter=redis.info[*], ( redis-cli -p {{ redis_server_port }} info "$1" || echo "$1:0" ) | grep "^$1:" | cut -d: -f2
```

UserParameter=redis.role, ( redis-cli -p {{ redis_server_port }} info replication || echo 'role:unknown' ) | grep '^role:' | cut -d: -f2
UserParameter=redis.used_memory, ( redis-cli -p {{ redis_server_port }} info memory || echo 'used_memory:0' ) | grep '^used_memory:' | cut -d: -f2
UserParameter=redis.repl_backlog_size, ( redis-cli -p {{ redis_server_port }} info replication || echo 'repl_backlog_size:0' ) | grep '^repl_backlog_size:' | cut -d: -f2
UserParameter=redis.repl_backlog_active, ( redis-cli -p {{ redis_server_port }} info replication || echo 'repl_backlog_active:0' ) | grep '^repl_backlog_active:' | cut -d: -f2

Macros:
{$REDIS_MEM_CRIT}
{$REDIS_MEM_WARN}
{$REDIS_PORT}

Items:

tcp_connect_check[localhost,{$REDIS_PORT},1]
redis.role
redis.repl_backlog_size
redis.used_memory
redis.repl_backlog_active

Triggers:

{redis-server:tcp_connect_check[localhost,{$REDIS_PORT},1].last()}<>0

{redis-server:redis.used_memory.last()} - {redis-server:redis.repl_backlog_size.last()}*{redis-server:redis.repl_backlog_active.last()}>{$REDIS_MEM_CRIT}

{redis-server:redis.used_memory.last()} - {redis-server:redis.repl_backlog_size.last()}*{redis-server:redis.repl_backlog_active.last()}>{$REDIS_MEM_WARN}

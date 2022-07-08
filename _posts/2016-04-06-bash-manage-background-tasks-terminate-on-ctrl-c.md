---
layout: post
title:  "bash: manage background tasks and terminate them all on Ctrl+C"
tags: bash
comments_by_utterance: true
---
Run multiple background tasks in bash and gather every task exit code:

```bash
declare -A process
declare -A result

for host in $hosts; do

ssh -o ConnectTimeout=10 "$host" /bin/task &
process["$host"]=$!

done

# Get results
for host in $hosts; do
    wait ${process["$host"]}
    result["$host"]=$?
    [ ${result["$host"]} -eq 0 ] && echo "OK: $host" || echo "ERROR: $host"
done
```

Yes, you can use associative arrays in bash >= 4.0.

Terminate all background tasks if main script was interrupted by Ctrl+C:

```bash
function term_all_processes() {
	echo "Sending TERM signal to all background jobs..."
	for proc in $(jobs -lp); do
		echo "Stopping PID $proc"
		kill -TERM $proc
	done
	exit 1
}
trap term_all_processes INT
```

Bash has `trap` built-in that allows to create custom handlers for recieved signals. `Ctrl+C` actually is terminal escape sequence that generates SIGINT.

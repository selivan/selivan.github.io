For example, backup mysql binary logs.

Note: if you need redundancy, you should use RAID.

```bash
#!/bin/bash

src_dir=/var/lib/mysql/bin-logs
dest_dir=/srv/backup/bin-logs
delay=0.1
lockfile=/tmp/backup-binlogs.flock

if ! flock -n "$lockfile" true; then
    echo  "ERROR: other instance already has lock on $lockfile"
    exit 1
fi

while true; do
    # --append append data onto shorter files !! DOESN'T WORK FOR BINLOGS: FILES DIFFER
    # --quiet supress non-error messages
    # --recursive recurse into directories
    # --size-only skip files that match in size
    # --inplace update destination files in-place
    # --no-whole-file do not copy files whole (w/o delta-xfer algorithm).
    # --whole-file is rsync default is both source and destination are local
    # See https://superuser.com/a/674634/100108
    ionice -c 3 rsync --quiet --recursive --size-only --inplace --no-whole-file "$src_dir"/ "$dest_dir"/
    # rsync exit code 20 means process is stopped with SIGTERM or SITINT
    test $? -eq 20 && break
    sleep "$delay"
done
```

```ini
[Unit]
Description=Syncronize bin logs to backup storage
After=nvme-initilize.service

[Service]
ExecStart=/usr/local/bin/backup-binlogs.sh
Type=simple
# Default is KillMode=cgroup, that kills all rsync processes not allowing to finish the job correctly
KillMode=process

User=root
Group=root

[Install]
WantedBy=multi-user.target
```

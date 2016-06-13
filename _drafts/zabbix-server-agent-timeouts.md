https://support.zabbix.com/browse/ZBX-10868
http://serverfault.com/questions/780012/zabbix-adding-items-make-agents-not-available
https://www.zabbix.com/documentation/3.0/manual/config/items/queue
https://www.zabbix.com/documentation/3.0/manual/appendix/items/unreachability

`Timeout` on server specifies how long we wait for agent, SNMP device or external check.

`Timeout` on agent: Spend no more than seconds on processing.

A host is treated as unreachable after a failed check (network error, timeout) by Zabbix, SNMP, IPMI or JMX agents. Active checks do not influence host availability in any way.

From that moment `UnreachableDelay` defines how often a host is rechecked using one of the items (including LLD rules) in this unreachability situation and such rechecks will be performed already by unreachable pollers. By default it is 15 seconds before the next check.

The `Timeout` parameter will also affect how early a host is rechecked during unreachability. If the `Timeout` is 20 seconds and `UnreachableDelay` 30 seconds, the next check will be in 50 seconds after the first attempt.

The `UnreachablePeriod` parameter defines how long the unreachability period is in total. By default `UnreachablePeriod` is 45 seconds. `UnreachablePeriod` should be several times bigger than `UnreachableDelay`, so that a host is rechecked more than once before a host becomes unavailable.

After the `UnreachablePeriod` ends and the host has not reappeared, the host is treated as unavailable. Frontend host availability icon becomes red. Logs:

```
temporarily disabling Zabbix agent checks on host "New host": host unavailable
```

`UnavailableDelay` parameter defines how often a host is checked during host unavailability.

After enabling item that doesn't feet timeout:

Logs:

Zabbix agent item "net.tcp.port[192.168.56.103,410]" on host "zabbix-agent" failed: first network error, wait for 15 seconds

Values processed by Zabbix server per second: zabbix[wcache,values] goes down

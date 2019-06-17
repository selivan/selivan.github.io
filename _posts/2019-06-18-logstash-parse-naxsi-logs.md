---
layout: post
title:  "Parsing Naxsi messages in nginx error log with Logstash"
tags: [logstash,grok,nginx,naxsi]
---

[Naxsi](https://github.com/nbs-system/naxsi) open-source Web Application Firewall by [nbs-system](https://www.nbs-system.com/en/) prints it's error messages to nginx error log.

Here is Logstash config to parse it. I tried making it complaint to [Elastic Common Schema](https://www.elastic.co/guide/en/ecs/current/) - open specification on set of fields to use when storing logs and metrics in Elasticsearch.

```ini
filter {
    # Condition to separate nginx error logs from other logs in your configuration
        grok {
            named_captures_only => true
            # From most specific pattern to least specific
            match => {
                "message" => [
                    "(?<nginx.error.time>%{YEAR}/%{MONTHNUM}/%{MONTHDAY} %{HOUR}:%{MINUTE}:%{SECOND}) \[%{WORD:log.level}\] %{POSINT:process.pid:int}#%{NUMBER:process.thread.id:int}\: \*%{NUMBER:nginx.error.connection_id:int} (?<message>(?<[@metadata][naxsi_log_type]>NAXSI_EXLOG|NAXSI_FMT): %{GREEDYDATA:[@metadata][naxsi_message]}), client: %{IP:nginx.error.client}, server: %{HOSTNAME:nginx.error.server}, request: \"(?<request>[^\"]*)\", host: \"%{HOSTNAME:nginx.error.host}\"(, referrer: \"(?<nginx.error.referrer>[^\"]*)\")?",

                    "(?<nginx.error.time>%{YEAR}/%{MONTHNUM}/%{MONTHDAY} %{HOUR}:%{MINUTE}:%{SECOND}) \[%{WORD:log.level}\] %{POSINT:process.pid:int}#%{NUMBER:process.thread.id:int}\: \*%{NUMBER:nginx.error.connection_id:int} %{GREEDYDATA:message}, client: %{IP:nginx.error.client}, server: %{HOSTNAME:nginx.error.server}, request: \"%{GREEDYDATA:request}\", upstream: \"%{GREEDYDATA:nginx.error.upstream}\"",

                    "(?<nginx.error.time>%{YEAR}/%{MONTHNUM}/%{MONTHDAY} %{HOUR}:%{MINUTE}:%{SECOND}) \[%{WORD:log.level}\] %{POSINT:process.pid:int}#%{NUMBER:process.thread.id:int}\: \*%{NUMBER:nginx.error.connection_id:int} %{GREEDYDATA:message}, client: %{IP:nginx.error.client}, server: %{HOSTNAME:nginx.error.server}, request: \"%{GREEDYDATA:nginx.error.request}\"",

                    "(?<nginx.error.time>%{YEAR}/%{MONTHNUM}/%{MONTHDAY} %{HOUR}:%{MINUTE}:%{SECOND}) \[%{WORD:log.level}\] %{POSINT:process.pid:int}#%{NUMBER:process.thread.id:int}\: \*%{NUMBER:nginx.error.connection_id:int} %{GREEDYDATA:message}",

                    "(?<nginx.error.time>%{YEAR}/%{MONTHNUM}/%{MONTHDAY} %{HOUR}:%{MINUTE}:%{SECOND}) \[%{WORD:log.level}\] %{GREEDYDATA:message}"
                ]
            }
            # tag_on_failure => [ "_grokparsefailure" ]
            overwrite => [ "message" ]
        }
        if [@metadata][naxsi_message] {
            kv {
                source => "[@metadata][naxsi_message]"
                field_split => "&"
                value_split => "="
                target => "naxsi"
                # tag_on_failure => "_kv_filter_error"
                # tag_on_timeout => "_kv_filter_timeout"
            }
            mutate {
              add_field => {
                "[naxsi][log_type]" => "%{[@metadata][naxsi_log_type]}"
              }
            }
            if [naxsi][id] {
              mutate {
                convert => {
                  "[naxsi][id]" => "integer"
                }
              }
            }
        }
        if [nginx.error.time] {
            date {
                match => [ "nginx.error.time", "yyyy/MM/dd HH:mm:ss" ]
                target => "@timestamp"
                # tag_on_failure => [ "_dateparsefailure" ]
            }
        }
}
```

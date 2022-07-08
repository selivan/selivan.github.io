---
layout: post
title:  "Logstash: parse mysql slow log"
tags: [logstash,grok,mysql]
comments_by_utterance: true
---
We send mysql slow log to logstash with rsyslog, as a whole multi-line message. So it should be parsed as single message, logstash [multiline plugin](https://www.elastic.co/guide/en/logstash/current/plugins-codecs-multiline.html) is useless in this case.

I couldn't google up apropriate grok pattern, so I spent some time creating it. Here it is, so you don't have to lose that time again.

```bash
grok {
    match => {
        # !! REMOVE NEW LINES FROM PARSER STRING
        # They were added for readability
        "message" => "
        (?m)^# Time: (?<time>%{NUMBER}%{SPACE}%{TIME})\n
        # User@Host: %{USER:mysql_user}\[%{USER:mysql_current_user}\] @ (?<mysql_client_host>%{HOSTNAME}|%{IP}) \[%{IP:mysql_client_ip}\]\n
        # Thread_id:%{SPACE}%{INT:thread_id} %{SPACE}Schema:%{SPACE}(%{WORD:schema})?%{SPACE}Last_errno:%{SPACE}%{INT:last_errno}%{SPACE}Killed:%{SPACE}%{INT:killed}\n
        # Query_time:%{SPACE}%{NUMBER:query_time}%{SPACE}Lock_time:%{SPACE}%{NUMBER:lock_time}%{SPACE}Rows_sent:%{SPACE}%{INT:rows_sent}%{SPACE}Rows_examined:%{SPACE}%{INT:rows_examined}%{SPACE}Rows_affected:%{SPACE}%{INT:rows_affected}%{SPACE}Rows_read:%{SPACE}%{INT:rows_read}\n
        # Bytes_sent:%{SPACE}%{INT:bytes_sent}\nSET timestamp=%{INT:mysql_timestamp};\n
        %{GREEDYDATA:query}"
    }
}
date {
    match => [ "time", "YYMMdd HH:mm:ss", "YYMMdd  H:mm:ss" ]
    remove_field => [ "time" ]
}
```

Unfortunately, logstash config syntax, besides just being ugly(why not use yaml or other well-known format for structured data?) does not allow to write long strings in convenient multi-line form, like `'''..'''` in python(see this [unanswered question](https://discuss.elastic.co/t/syntax-for-readable-long-lines-in-logstash-config/88754) on discuss.elastic.co). So don't forget to remove new lines I added for readability.

---
layout: post
title:  "Graylog pitfalls"
tags: graylog
---
* If extractor fails - message is not saved. For safety use regex check in every extractor. It may affect performance, but all your messages will be saved.
* If you are extracting timestamp and it does not contain explicit timezone, it alwaus defaults to UTC. Even if you configured your timezone in graylog settings. So always denote correct timezone in timestamp extractor.
* If you are extracting timestamp - be cateful: some software prints timestamps like 07:08:01, but other uses 7:08:01 for hours 0-9.
* No central config for sender address, you should define it for every alert
* Graylog server does not understand SIGHUP, you have to reload it.
* 
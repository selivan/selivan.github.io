---
layout: post
title:  "Ansible snippet to update Elasticsearch cluster settings"
tags: [ ansible, elasticsearch ]
comments_by_utterance: true
---

Ansible snippet to update Elasticsearch [cluster settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-update-settings.html).

Updates settings only if required, works correctly with check mode.

Uses curl, because ansible `get_url` module does not support saving request result anywhere except a file.

```yaml
{% raw %}
- name: get elasticsearch settings
  shell: curl --silent "http://127.0.0.1:9200/_cluster/settings"
  args:
    warn: false
  register: get_es_settings
  check_mode: False
  changed_when: False
  tags: elk-elasticsearch-cluster-settings

- set_fact:
    es_settings: "{{ get_es_settings.stdout | from_json }}"
  check_mode: no
  tags: elk-elasticsearch-cluster-settings

- name: set elasticsearch settings only if it differs
  shell: >-
    curl --silent -XPUT 'http://127.0.0.1:9200/_cluster/settings' -H 'Content-Type: application/json'
    --data '{ "persistent": { "{{ item.key }}": "{{ item.value }}" } }'
  args:
    warn: false
  loop: "{{ elk_elasticsearch_cluster_settings | dict2items }}"
  when: es_settings['persistent'].{{ item.key }} != "{{ item.value }}"
  tags: elk-elasticsearch-cluster-settings
{% endraw %}
```

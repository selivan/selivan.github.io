---
layout: post
title:  "Jinja 2 delete an item from dictionary inside a template"
tags: [ jinja, jinja2, ansible ]
---

How to delete an item from a dictionary inside jinja2 template?

I couldn't find it in [jinja2 documentation](https://jinja.palletsprojects.com/en/master/), but seems that jinja2 assignments support python methods for dictionaries. `del` statement won't work, but this will:

```jinja
{% set _dummy = mydict.pop('key') %}
{% if 'key' not in mydict %}
'key' was deleted
{% endif %}
```

To avoid using unnecessary variable, you may enable jinja `jinja2.ext.do` extension. For ansible, this is done with `jinja2_extensions` [configuration directive](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_JINJA2_EXTENSIONS). That makes code look clearer:

```jinja
{% do mydict.pop('key') %}
{% if 'key' not in mydict %}
'key' was deleted
{% endif %}
```

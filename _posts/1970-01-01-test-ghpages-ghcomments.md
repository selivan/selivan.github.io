---
layout: post
title:  "test-ghpages-ghcomments"
comments_by_disqus: false
---

Testing [ghpages-ghcomments](http://downtothewire.io/ghpages-ghcomments).

{% comment %}
{% unless page.comments_by_disqus | default: false %}
{% assign gpgc_post_title = page.id | prepend: 'Comments for ' %}
{% include gpgc_comments.html post_title=gpgc_post_title %}
{% endunless %}
{% endcomment %}

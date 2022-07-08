---
layout: post
title:  "AWS SES and WorkMail for the same domain in different regions"
tags: [aws,ses,workmail]
comments_by_utterance: true
---

Let's say you are already using SES to send out mail for your domain `example.com`. You verified the domain ownership by creating DNS TXT record `_amazonses.example.com` with required value. After some arguing with AWS support you got it out of sandbox. (Sometimes they refuse to do it for a long time, sometimes they do it on a first request. I supppose, they just roll a dice).

Now you want a WorkMail account to get mail for the same domain, and you create it in different region than the SES record. The thing is, WorkMail automatically creates a SES record in the same region. It requires this record to work, deleting it will break the WorkMail. This new SES record also belongs to `example.com`, but it is in sanbox, and it breaks your first SES record, because it sets `_amazonses.example.com` to another value.

To get this all working together, you may create DNS TXT record `_amazonses.example.com` with multiple values. In Route53  interface you can do it by enclosing both requred values in double quotes with a new line between them.

Or you can just use SES and WorkMail for a single domain always in the same region(which would probably save me some headache).

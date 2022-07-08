---
layout: post
title:  "APT repository signing key id for ansible"
tags: [ansible,apt,gpg]
comments_by_utterance: true
---
I've got tired of googling each time I manage apt repositories with ansible, so I put it here.

Ansible [apt_key](https://docs.ansible.com/ansible/latest/modules/apt_key_module.html) module requires key id to correctly report changed state. Without it the task is always marked as changed.

OpenPGP key fingerprint is usually written as 10 groups of 4 hexadecimal characters(160-bit value): `72EC F46A 56B4 AD39 C907  BBB7 1646 B01B 86E5 0310`. OpenPGP long key id is last 16 characters(4 groups), and short key id is last 8 characters(2 groups). Short keys are [not recommended](https://security.stackexchange.com/questions/74009/what-is-an-openpgp-key-id-collision) for security reasons.

```
curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | tee yarn.asc | gpg --keyid-format long

gpg: WARNING: no command supplied.  Trying to guess what you mean ...
pub   rsa4096/1646B01B86E50310 2016-10-05 [SC]
      72ECF46A56B4AD39C907BBB71646B01B86E50310
uid                           Yarn Packaging <yarn@dan.cx>
sub   rsa4096/02820C39D50AF136 2016-10-05 [E]
sub   rsa4096/D101F7899D41F3C3 2016-10-05 [S] [expired: 2017-10-05]
sub   rsa4096/46C2130DFD2497F5 2016-10-30 [S] [expired: 2019-01-01]
sub   rsa4096/E074D16EB6FF4DE3 2017-09-10 [S] [expired: 2019-01-01]
sub   rsa4096/23E7166788B63E1E 2019-01-02 [S] [expires: 2021-02-03]
sub   rsa4096/4F77679369475BAA 2019-01-11 [S] [expires: 2021-02-03]
              ^--------------^
```

If there are multiple subkeys, use the one that expires later. To remove apt key, use the id of public master key(pub).

So installing apt repository in ansible should look like this:

```yaml
{% raw %}
- name: yarn apt key
  apt_key:
    id: 4F77679369475BAA
    data: "{{ lookup('file', 'yarn.asc') }}"
    keyring: /etc/apt/trusted.gpg.d/yarn.gpg

- name: yarn apt repository
  apt_repository:
    filename: yarn
    repo: "deb http://dl.yarnpkg.com/debian/ stable main"
    state: present
    update_cache: yes

- name: install yarn
  apt:
    state: present
    pkg:
      - yarn
{% endraw %}
```

I prefer using separate file in `/etc/apt/trusted.gpg.d` to storing all keys in `/etc/apt/trusted.gpg`. It's more obvious and easier to manage.

---
layout: post
title:  "Using Ansible dynamic AWS EC2 inventory with encrypted credentials in vault"
tags: [ansible,aws,ec2,ansible-vault]
comments_by_utterance: true
---
**UPD**: The most secure way is to create instance with IAM role and run ansible on it. But sometimes it is not convenient.

---

Ansible dynamic inventory script for AWS EC2 requires either to store credentials in plain text in `~/.aws/credentials`, or to manually export them in shell variables.

I prefer to store all security sensitive data in vault encrypted files, including AWS credentials. Here is how you can do it.

**NOTE**: This setup will work only if you are using vault password file or executable to get it, without interactive typing in console.

Credentials are stored in file `aws_credentials.vault.yml` in this form:

```yaml
aws_access_key: XXXXXXXXXXXXX
aws_secret_key: YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

In `ansible.cfg` we set inventory path to directory with our inventory files, both static and dynamic:

```ini
[defaults]
inventory=inventory
```

`inventory/static`: static hosts definition. It should have at least localhost defined.

`inventory/ec2.py.orig` - here we store original [EC2 external inventory](https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py) script. Files with extensions `.ini`, `.orig`, `.txt`, `.pyc` and [some others](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html#using-inventory-directories-and-multiple-inventory-sources) are ignored as inventory source. It won't be used directly.

`inventory/ec2.ini` - [ec2.ini](https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.ini) to configure EC2 external inventory script.

Now let's create executable to use `ec2.py.orig` with credentials from ansible vault.

`inventory/ec2.sh`:

```bash
#!/bin/bash
cd "$(dirname $0)/.."

# Set inventory to localhost only to avoid recursion on inventory lookup
credentials=$(ansible localhost --inventory='localhost,' --connection=local --extra-vars=@aws-credentials.vault.yml -m debug -a 'msg="{% raw %}{{ aws_access_key }}:{{ aws_secret_key }}{% endraw %}"' | tr -d ' ' | grep '"msg":' | cut -d'"' -f4)

export AWS_ACCESS_KEY_ID=$(echo $credentials | cut -d: -f1)
export AWS_SECRET_ACCESS_KEY=$(echo $credentials | cut -d: -f2)
export EC2_INI_PATH="$(dirname $0)/inventory/ec2.ini"

exec inventory/ec2.py.orig
```

Don't forget `chmod a+x inventory/ec2.sh`, or Ansible will try to read it as static file.

This executable uses ansible to read AWS credentials from vault encrypted file and passes them to EC2 external inventory script with environment variables. Inventory is explcitly set to localhost only to prevent recursion on trying to read inventory.

Links:
* [Ansible documentation - Dynamic Inventory](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html)

---
layout: post
title:  "VSCode: open ansible files with right syntax"
tags: [vscode,ansible]
comments_by_utterance: true
---

**UPD**: Added identation settings for ansible.

VSCode [extension for Ansible](https://marketplace.visualstudio.com/items?itemName=vscoss.vscode-ansible#user-content-syntax-highlighting) from Microsoft suggestes to open all `*.yml` files with ansible syntax:

```json
"files.associations": {
        "**/*.yml": "ansible"
    },
```

This is too wide: you may have YAML files that are not related to ansible.

Also, you need correct syntax highlighting for variables in `vars`, `defaults`, `group_vars`, etc. I recommend [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extension which supports combined yaml+jinja syntax.

Here is mode precise options to use ansible and yaml+jinja syntax only for right files:

```json
"files.associations": {
    // Ansible
    "**/defaults/**/*.yml": "jinja-yaml",
    "**/group_vars/**/*": "jinja-yaml",
    "**/host_vars/**/*": "jinja-yaml",
    "**/vars/**/*.yml": "jinja-yaml",
    "**/tasks/**/*.yml": "ansible",
    "**/handlers/*.yml": "ansible",
    "**/meta/*.yml": "ansible",
    "**/roles/**/*.yml": "ansible",
    "**/playbooks/**/*.yml": "ansible",
    "**/ansible/**/hosts": "ini",
    "**/ansible/**/inventory": "ini",
    "ansible.cfg": "ini",
},
```

Also you might like to set identation settings for "ansible" language:

```json
"[ansible]": {
    "editor.detectIndentation": false,
    "editor.tabSize": 2,
    "editor.insertSpaces": true
},
```

Open File -> Preferences -> Settings( `Ctrl + ,` ), search for "Files: Associations", click on "Edit in settings.json".

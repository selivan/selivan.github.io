---
layout: post
title:  "Install jekyll and github-pages on Ubuntu 14.04 Trusty"
tags: jekyll
comments_by_utterance: true
---
Task: install jekyll with github-pages extenshions on Ubuntu 14.04 Trusty.

In trusty repositories maximum available ruby version is 1.9. Github Pages [started using jekyll 3.0](https://github.com/blog/2100-github-pages-now-faster-and-simpler-with-jekyll-3-0) on May 1st 2016 (see current [dependencies and versions](https://pages.github.com/versions/)). It requires at least ruby 2.0.

Add ppa with stable ruby versions built by [this guys](https://www.brightbox.com/docs/ruby/ubuntu/) and install it:

```bash
sudo apt-add-repository ppa:brightbox/ruby-ng; sudo apt-get update
sudo apt-get install ruby2.3 ruby2.3-dev ruby-switch
```

With `ruby-switch` you can have multiple ruby versions installed and select one of them as default.

Now we have to install required gems. I don't want to create chaos of ruby gems installed from debian packages and manually, so I prefer to keep all required gems in `$HOME/.gem` directory:

```bash
gem install github-pages --user-install --no-rdoc --no-ri
```

Now you can run jekyll with github-pages support. It may be convenient to create separate script for this and put it into root of your github pages repository:

```bash
#!/bin/bash
export PATH="$(ruby -rubygems -e 'puts Gem.user_dir')/bin:$PATH"
jekyll serve -w
```

To update your setup to latest github-pages version, you can just do

```bash
gem update github-pages --user-install --no-rdoc --no-ri
```

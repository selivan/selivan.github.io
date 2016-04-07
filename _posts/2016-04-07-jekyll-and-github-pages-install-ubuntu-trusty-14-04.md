---
layout: post
title:  "Install jekyll and github-pages on Ubuntu 14.04 Trusty"
categories: jekyll
---
Task: install jekyll with github-pages extenshions on Ubuntu 14.04 Trusty.

In trusty repositories maximum available ruby version is 1.9. Github Pages uses jekyll 3 (see [dependencies and versions](https://pages.github.com/versions/)), which requires at least ruby 2.0.

Add ppa with stable ruby versions built by [this guys](https://www.brightbox.com/docs/ruby/ubuntu/) and install it:

```
apt-add-repository ppa:brightbox/ruby-ng; apt-get update
apt-get install ruby2.3 ruby2.3-dev ruby-switch
```  

With `ruby-switch` you can have multiple ruby versions installed and select one of them as default.

Now we have to install required gems. I don't want to create chaos of ruby gems installed from debian packages and manually, so I prefer to keep all required gems in home dir:

```
gem install --user-install github-pages --no-rdoc --no-ri
```

Now you can run jekyll with github-pages support. It may be convenient to create separate script for this and put it into root of your github pages repository:

```bash
export PATH="$(ruby -rubygems -e 'puts Gem.user_dir')/bin:$PATH"
jekyll -w
```
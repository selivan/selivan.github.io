#!/bin/bash
# I have jekyll and dependant ruby gems installed in home dir to keep base system clean

export PATH="$(ruby -r rubygems -e 'puts Gem.user_dir')/bin:$PATH"
jekyll serve -w


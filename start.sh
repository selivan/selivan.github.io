#!/bin/bash
# I use jekyll and dependant ruby gems installed in home dir to keep system clean

export PATH="$(ruby -rubygems -e 'puts Gem.user_dir')/bin:$PATH"
jekyll serve -w


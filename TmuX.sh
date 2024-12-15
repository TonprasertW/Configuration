#!/usr/bin/bash

sudo apt-get install tmux

# setup term
touch ~/.tmux.conf
echo "set -g default-terminal "screen-256color"
      set -ga terminal-overrides ",xterm-256color:Tc" " > ~/.tmux.conf

# lauch a tmux session
tmux
tmux source-file ~/.tmux.conf

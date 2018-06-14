#!/bin/bash
if [[ $(ps -a | grep "[q]q_bot" | wc -l) -ge "1" ]];then
  for id in $(ps -a | grep "[q]q_bot" | awk '{print $1}');do
    echo "kill old, $id"
    kill $id
  done
fi

pybin="/Users/ytl/.pyenv/versions/3.6.5/bin/python3"
$pybin /Users/ytl/YTL/Project/chatfs/qq_bot.py &
#~/.ytl/bin/alert "restart qq_bot"

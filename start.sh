#!/bin/bash
if [[ $(ps -a | grep qq_bot | wc -l) -eq "2" ]];then
  id=$(ps -a | grep qq_bot | awk 'NR==1 {print $1}')
  echo "kill old, $id"
  kill $id
fi

pybin="/Users/ytl/.pyenv/versions/3.6.5/bin/python3"
$pybin /Users/ytl/YTL/Project/chatfs/qq_bot.py &
#~/.ytl/bin/alert "restart qq_bot"

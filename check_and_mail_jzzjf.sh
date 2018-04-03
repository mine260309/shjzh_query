#!/usr/bin/env bash

# Please set env for below:
# * shjzz_username - Your ID
# * shjzz_password - Your password in the jzh system
# * shjzz_mailto - The email address to notify

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

n=0
until [ $n -ge 5 ] # Retry for at most 5 times
do
  r=`python3 $DIR/query_score.py -q`
  if [ $? -eq 0 ]; then
    break
  fi
  n=$[$n+1]
  sleep 15
done

if [ $n -lt 5 ]; then
  mail -s "\"Shangh JZZJF result: $r\"" -t $shjzz_mailto <<< "" && echo "Success"
else
  echo "Failed"
fi


#!/usr/bin/env bash

# Please set env for below:
# * shjzh_username - Your ID
# * shjzh_password - Your password in the jzh system
# * shjzh_mailto - The email address to notify

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

n=0
until [ $n -ge 5 ] # Retry for at most 5 times
do
  r=`python3 $DIR/query.py -q`
  if [ $? -eq 0 ]; then
    break
  fi
  n=$[$n+1]
  sleep 15
done

if [ $n -lt 5 ]; then
  mail -s "\"Shangh JZH result: $r\"" -t $shjzh_mailto <<< "" && echo "Success"
else
  echo "Failed"
fi


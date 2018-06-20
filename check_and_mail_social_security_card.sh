#!/usr/bin/env bash

# Please set env for below:
# * sbk_name - Your name
# * sbk_id - Your id
# * sbk_mailto - The email address to notify

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The name shall be in utf8, and the website expects gb2312
n=`echo $sbk_name | recode utf8..gb2312`
r=`curl -G --data-urlencode "name=$n" --data-urlencode "registerCode=$sbk_id" "http://www.962222.net/sbkRS.jsp" | grep "result11" | tr -d '[:space:]' | sed -e 's/<[^>]*>//g' | sed -e "s/&nbsp;//g"`

#echo $sbk_name $r

mail -s "\"Shanghai sbk result: $sbk_name $r\"" -t $sbk_mailto <<< "" && echo "Success"


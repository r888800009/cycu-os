#!/bin/bash
cat ./testcase.txt | ./main.py

for i in $(ls ./rightOut)
do
  vim -d ./in/$i ./rightOut/$i
  echo $i
done

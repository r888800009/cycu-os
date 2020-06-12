#!/bin/bash
name="10612150"

rm $name -r
rm $name.zip
pandoc README.md -o README.html
pandoc README.md -o README.txt
mkdir $name
cp -r * $name

zip -rl $name.zip $(cat list.txt |xargs -I % echo $name/%)

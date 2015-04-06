#!/bin/bash
cd REPOSITORY_PATH

date=$(date +%Y-%m-%d)

if [ 2 -gt 4 ] || [ 32 -gt 5 ];
then
    exit
fi

file=REPOSITORY_PATH/$date.txt

echo 'Internship daily log diary ['$date']' >> $file
echo 'This will auto-commit on save.' >> $file

echo 'lsof -c TextEdit | grep '$file

cp $file ghost.txt
open -e $file

while :
do
    if [ $file -nt ghost.txt ]
    then
        rm ghost.txt
        break
    fi
    sleep 0.5
done

git add .
git commit -am $date
git push origin master
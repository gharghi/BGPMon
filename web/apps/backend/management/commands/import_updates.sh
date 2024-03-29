#!/usr/bin/env bash

dir=/shahin/BGPMon/web/apps/backend
#dir=/Users/shahin/Documents/Projects/BGPMon/web/apps/backend
rm $dir/tmp/latest-update.gz
rm $dir/tmp/out.csv
wget -P $dir/tmp/ http://data.ris.ripe.net/rrc00/latest-update.gz
bgpdump -m $dir/tmp/latest-update.gz | sed "s/||/|0|/g" | awk  -F '|' {' if ($3 == "A") print $2 "|" $5 "|" $6 "|" $7 "|" $6'} > $dir/tmp/out.csv
mysql -u root -p"0300301" -D bgpmon -e "truncate table main_app_dump"
mysql -u root -p"0300301" -D bgpmon -e "LOAD DATA INFILE '$dir/tmp/out.csv' INTO TABLE main_app_dump FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n' IGNORE 1 LINES (time, asn, @var1, path, prefix) SET network = INET6_ATON(SUBSTRING(@var1, 1, POSITION('/' in @var1) - 1)); "

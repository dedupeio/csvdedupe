#!/bin/bash

cat Lobbyists_2012_present.csv | \
csvpys -s "Full Address" "ch['CLIENT ADDRESS'] + ' ' + ch['CLIENT ADDRESS 2']" | \
csvpys -s "Client Industry" "ch['CLIENT OTHER INDUSTRY'] if ch['CLIENT INDUSTRY'] == 'OTHER' else ch['CLIENT INDUSTRY']" | \
sed '1 s/$/,"Vendor ID"/' | \
sed '2,$s/$/,,/' | \
csvcut -c "CLIENT NAME","Full Address","CLIENT CITY","CLIENT STATE","CLIENT ZIP","Vendor ID","Client Industry" | \
csvsort | \
uniq > lobbyists.csv

cat Contracts_after_8_2010.csv | \
csvpys -s "Full Address" "ch['Address 1'] + ' ' + ch['Address 2']" | \
sed '1 s/$/,"Client Industry"/' | \
sed '2,$s/$/,/' | \
csvcut -c "Vendor Name","Full Address","City","State","Zip","Vendor ID","Client Industry" | \
csvsort | \
uniq > contracts.csv

csvstack -g lobbyists,contracts -n source lobbyists.csv contracts.csv > stacked.csv

cat stacked.csv | csvdedupe --config config.json -v > output.csv


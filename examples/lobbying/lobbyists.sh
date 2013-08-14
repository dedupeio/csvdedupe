#!/bin/bash

cat Lobbyists_2012_present.csv | \
csvpys -s "Full Address" "ch['CLIENT ADDRESS'] + ' ' + ch['CLIENT ADDRESS 2']" > \
full_lobbyists.csv

cat full_lobbyists.csv | \
sed '1 s/$/,"Vendor ID"/' | \
sed '2,$s/$/,,/' | \
csvcut -c "CLIENT NAME","Full Address","CLIENT CITY","CLIENT STATE","CLIENT ZIP","Vendor ID" | \
csvsort | \
uniq > lobbyists.csv

cat Contracts_after_8_2010.csv | \
csvpys -s "Full Address" "ch['Address 1'] + ' ' + ch['Address 2']" > \
full_contracts.csv 

cat full_contracts.csv | \
csvsort -c "Vendor ID" | \
csvgroup -c "Vendor ID" -a common "Vendor Name","Full Address","City","State","Zip" | \
csvcut -c "Vendor Name","Full Address","City","State","Zip","Vendor ID" > \
contracts.csv

csvstack -g lobbyists,contracts -n source lobbyists.csv contracts.csv > \
stacked_lobbyists_contracts.csv

cat stacked_lobbyists_contracts.csv | \
csvdedupe --config lobbyists_contracts_config.json -v > output1.csv

csvgrep -c "Cluster ID" -r "[^x]" output1.csv > clusters.csv

csvgrep -c "Vendor ID" -r ".+" clusters.csv | \
csvcut -c "Cluster ID","Vendor ID" > clusters_left.csv

csvgrep -c "Vendor ID" -r "^$" clusters.csv | \
csvpys -s "client_info" "ch['CLIENT NAME'] + ch['Full Address'] + ch['CLIENT CITY'] + ch['CLIENT STATE'] + ['CLIENT ZIP']" | \
csvcut -c "Cluster ID","client_info" > clusters_right.csv

csvjoin clusters_left.csv clusters_right.csv -c "Cluster ID" > lobbyists_contract_linking.csv

cat full_lobbyists.csv | \
sed '1 s/$/,"Vendor ID"/' | \
sed '2,$s/$/,,/' | \
csvcut -c "LOBBYIST LAST NAME","LOBBYIST FIRST NAME","LOBBYIST MIDDLE INITIAL","CLIENT NAME" | \
csvsort | \
uniq > lobbyists.csv

cat Lobbyist_Data_-_Lobbyist_Compensation_Report.csv | \
csvcut -c "LAST NAME","FIRST NAME","LOBBYIST MIDDLE INITIAL","CLIENT" | \
csvsort | \
uniq > compensation.csv

csvstack -g lobbyists,compensation -n source lobbyists.csv compensation.csv > \
stacked_lobbyists_compensation.csv

cat stacked_lobbyists_compensation.csv | \
csvdedupe --config lobbyists_compensation_config.json -v > output2.csv

csvgrep -c "Cluster ID" -r "[^x]" output2.csv | \
csvpys -s "lobbyist_name_client" "ch['LOBBYIST FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LOBBYIST LAST NAME'] + ch['CLIENT NAME']" | \
sed '1 s/Cluster ID/Client Relation/' | \
csvcut -c "Client Relation","lobbyist_name_client" > \
lobbyists_compensation_linking.csv

cat Lobbyist_Data_-_Lobbyist_Compensation_Report.csv | \
csvpys -s "lobbyist_name_client" "ch['FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LAST NAME'] + ch['CLIENT']" > \
compensation.csv

cat full_lobbyists.csv | \
csvpys -s "lobbyist_name_client" "ch['LOBBYIST FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LOBBYIST LAST NAME'] + ch['CLIENT NAME']" > \
full_lobbyists_id.csv

csvjoin compensation.csv lobbyists_compensation_linking.csv -c "lobbyist_name_client" | \
csvpys -s compensation "int(float(ch['COMPENSATION'][1:].replace(',', '')))" | \
csvgroup -c "Client Relation" -a sum "compensation" > \
rolled_up_compensation.csv




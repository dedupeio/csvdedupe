#!/bin/bash

# Analysis

csvjoin full_compensation_id.csv compensation_lobbyists_linking.csv -c "lobbyist_name_client" | 
csvpys -s compensation "int(float(ch['COMPENSATION'][1:].replace(',', '')))" | 
csvsort -c "Client Relation" | 
csvgroup -c "Client Relation" -a sum "compensation" > \
rolled_up_compensation.csv

cat full_contracts.csv | 
csvpys -s award "int(float(ch['Award Amount'][1:].replace(',', '')))" | 
csvsort -c "Vendor ID" | 
csvgroup -c "Vendor ID" -a sum "award" -a common "Vendor Name" > \
rolled_up_awards.csv

csvjoin full_lobbyists_id.csv contract_lobbyists_linking.csv -c "client_info" > full_lobbyists_id_a.csv

csvjoin full_lobbyists_id_a.csv compensation_lobbyists_linking.csv -c "lobbyist_name_client" | 
csvcut -c "Vendor ID","Client Relation" | 
csvsort | 
uniq > linking_table1.csv

csvjoin rolled_up_awards.csv linking_table1.csv -c "Vendor ID" > \
linking_table2.csv

csvjoin rolled_up_compensation.csv linking_table2.csv -c "Client Relation" | 
csvcut -c 1,3,5,2,4 > \
FINAL.csv


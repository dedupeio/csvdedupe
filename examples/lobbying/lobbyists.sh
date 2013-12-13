#!/bin/bash
rm lobbyist.db

#### Linking lobbyists and contract data

# Preprocess Addresses
cat Lobbyists_2012_present.csv | 
csvpys -s "Full Address" "ch['CLIENT ADDRESS'] + ' ' + ch['CLIENT ADDRESS 2']" > \
full_lobbyists.csv

csvsql --db sqlite:///lobbyist.db --table lobbyists\
       --insert full_lobbyists.csv 

cat Contracts_after_8_2010.csv | 
csvpys -s "Full Address" "ch['Address 1'] + ' ' + ch['Address 2']" > \
full_contracts.csv

csvsql --db sqlite:///lobbyist.db --table contracts\
       --insert full_contracts.csv 

csvsql --db sqlite:///lobbyist.db --table compensation\
       --insert Lobbyist_Data_-_Lobbyist_Compensation_Report.csv

# Align contracts and lobbyists and feed to dedupe

cat full_lobbyists.csv | 
sed '1 s/$/,"Vendor ID"/' | 
sed '2,$s/$/,,/' | 
csvcut -c "CLIENT NAME","Full Address","CLIENT CITY","CLIENT STATE","CLIENT ZIP","Vendor ID" | 
csvsort | 
uniq > lobbyists.csv

cat full_contracts.csv | 
csvsort -c "Vendor ID" | 
csvgroup -c "Vendor ID" -a common "Vendor Name","Full Address","City","State","Zip" | 
csvcut -c "Vendor Name","Full Address","City","State","Zip","Vendor ID" > \
contracts.csv

csvstack -g lobbyists,contracts -n source lobbyists.csv contracts.csv | 
csvdedupe --config contracts_lobbyists_config.json -v > output1.csv

# Reform output to linking table

# Remove unclustered data 
csvgrep -c "Cluster ID" -r "[^x]" output1.csv > vendor_clusters.csv

csvsql --db sqlite:///lobbyist.db --table vendor_cluster\
       --insert vendor_clusters.csv 

# #### Linking lobbyists and compensation data
rm lobbyists.csv

# group this by lobbyist id
cat full_lobbyists.csv | 
sed '1 s/$/,"Vendor ID"/' | 
sed '2,$s/$/,,/' | 
csvcut -c "LOBBYIST LAST NAME","LOBBYIST FIRST NAME","LOBBYIST MIDDLE INITIAL","CLIENT NAME" | 
csvsort | 
uniq > lobbyists.csv

cat Lobbyist_Data_-_Lobbyist_Compensation_Report.csv | 
csvcut -c "LAST NAME","FIRST NAME","LOBBYIST MIDDLE INITIAL","CLIENT" | 
csvsort | 
uniq > compensation.csv


csvstack -g lobbyists,compensation -n source lobbyists.csv compensation.csv | 
csvdedupe --config compensation_lobbyists_config.json -v > output2.csv

csvgrep -c "Cluster ID" -r "[^x]" output2.csv > lobbying_clusters.csv


csvsql --db sqlite:///lobbyist.db --table lobbying_cluster\
       --insert lobbying_clusters.csv 

select distinct "Lobbyist ID", vid from lobbyists inner join (select distinct "CLIENT NAME", "CLIENT CITY", "CLIENT STATE", "CLIENT ZIP", vid, "Full Address" from vendor_cluster inner join (select distinct "Vendor ID" as vid, "Cluster ID" from vendor_cluster where source="contracts") using ("Cluster ID") where source = "lobbyists") using ("CLIENT NAME", "CLIENT CITY", "CLIENT ZIP", "Full Address", "CLIENT STATE");


# # Since we need one, and only one column for linking we'll create
# # `lobbyist_name_client`
# csvgrep -c "Cluster ID" -r "[^x]" output2.csv | 
# csvpys -s "lobbyist_name_client" "ch['LOBBYIST FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LOBBYIST LAST NAME'] + ch['CLIENT NAME']" | 
# sed '1 s/Cluster ID/Client Relation/' | 
# csvcut -c "Client Relation","lobbyist_name_client" > \
# compensation_lobbyists_linking.csv

# ## Cleanup
# rm lobbyists.csv
# rm compensation.csv

# # Add linking ids
# cat Lobbyist_Data_-_Lobbyist_Compensation_Report.csv | 
# csvpys -s "lobbyist_name_client" "ch['FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LAST NAME'] + ch['CLIENT']" > \
# full_compensation_id.csv

# # could be problem with double counting here
# cat full_lobbyists.csv | 
# csvpys -s "client_info" "ch['CLIENT NAME'] + ch['Full Address'] + ch['CLIENT CITY'] + ch['CLIENT STATE'] + ch['CLIENT ZIP']" | 
# csvpys -s "lobbyist_name_client" "ch['LOBBYIST FIRST NAME'] + ch['LOBBYIST MIDDLE INITIAL'] + ch['LOBBYIST LAST NAME'] + ch['CLIENT NAME']" > \
# full_lobbyists_id.csv


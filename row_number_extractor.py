import json
import csv
import os

"""
extract_row_number(publisher_data) returns an integer number and the dictionary 
prefix_to_name_dict, containing a mapping between the prefixes and the names of 
the respective publishers. The integer retrieved is used as an index representing 
the number of the already successfully processed input rows. Accordingly, it is used 
to slice the input CSV file and process it only from the first unprocessed line on, 
in case the code run is interrupted. The additional function of this part of code is 
that of creating a dictionary for each publisher in publisher_data dictionary, 
exploiting the data provided in “publisher_data.csv”. 
"""


def extract_row_number(publisher_data):
    num = 0
    if not os.path.exists('publisher_data.csv'):
        return num, dict()
    else:
        with open('publisher_data.csv', 'r', encoding='utf8') as read_obj:
            dict_reader = csv.DictReader(read_obj)
            for pub in dict_reader:
                publisher_data[pub['name']] = {
                    "name": pub["name"],
                    "responsible_for_v": int(pub["responsible_for_v"]),
                    "responsible_for_i": int(pub["responsible_for_i"]),
                    "receiving_v": int(pub["receiving_v"]),
                    "receiving_i": int(pub["receiving_i"])
                }
                num += int(pub['responsible_for_i']) + int(pub['responsible_for_v'])

        with open("prefix_name.json", 'r', encoding='utf8') as fd:
            prefix_to_name_dict = json.load(fd)

        return num, prefix_to_name_dict

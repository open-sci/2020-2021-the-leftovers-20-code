import json
import csv
import os

"""
This function is aimed at returning an integer number, which is used as an index, in order to slice the input CSV file and process it only from the first still-non processed line on. The additional function of this part of code is that of creating and appending a dictionary for each publisher in publisher_data dictionary. In order to perform this set of actions, first of all a variable named num is initialized with the value 0, and then the existence in the directory of a file named “publisher_data.csv” is checked. In the case this file doesn’t exist, the variable num, whose value is 0, is returned. Since the output of this function is used as an index to individuate the last processed line of the CSV input file in the main function, in the case “publisher_data.csv” has not been created yet, no line of the original CSV has been processed, so the line to be processed is the first one. In the opposite case in which publisher_data.csv already exists, this file is read as a DictReader object, and for each element it contains, a key-value pair representing the publisher is added to publisher_data, whose key is the string of the name of the publisher, while the value is a dictionary with the following keys: “name”, “responsible_for_v”, “responsible_for_i”, “receiving_v”, “receiving_i”, and the associated values retrieved from the “publisher_data.csv” file. After the creation of this latter dictionary, the value of the variable num is updated by summing the value of “responsible_for_v” and the value of “responsible_for_i”. The sense of this passage is that of keeping track of the lines already processed in the original CSV file, and assuming that any citational data processed results in an increment by one either of the value of “responsible_for_v” or “responsible_for_i” in one publishers’ row in publisher_data.csv (read as a DictReader object),  by summing the values of 'responsible_for_i' and 'responsible_for_v' for each element of the DictReader object in a for loop it is possible to obtain the total number of citational data already processed. The final value of num at the end of the for loop is returned and used as start_index value in the main function.
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

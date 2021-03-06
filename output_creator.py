import json
import csv
import os

"""
create_output(publisher_data, output_json), is aimed at organizing all the collected data in order to store 
them in a JSON file, which is the output of the whole software execution. The purpose of this 
step is saving the obtained results in view of a maximization of the readability and the 
reusability of the extracted information. 
"""


def create_output(publisher_data, output_json):
    output_dict = {
        "citations": {
            "valid": list(),
            "invalid": list()
        },
        "publishers": list()
    }
    publisher_prefix_data = dict()

    with open("correct_dois.csv", 'r', encoding='utf8') as fd:
        total_correct = 0
        reader = csv.DictReader(fd)
        for row in reader:
            output_dict["citations"]["valid"].append(dict(row))
            total_correct += 1
        output_dict["total_num_of_valid_citations"] = total_correct

    with open("incorrect_dois.csv", 'r', encoding='utf8') as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            output_dict["citations"]["invalid"].append(dict(row))

    with open("prefix_member_code.json", 'r', encoding='utf8') as fd:
        data = json.load(fd)
        for key, value in data.items():
            if value not in publisher_prefix_data.keys():
                publisher_prefix_data[value] = [key]
            else:
                publisher_prefix_data[value].append(key)

    for pub in publisher_data.values():
        pub["prefix_list"] = publisher_prefix_data[pub["crossref_member"]]
        output_dict["publishers"].append(pub)

    with open("external_data.json", 'r', encoding='utf8') as fd:
        data = json.load(fd)
        output_dict["external_data_for_unrecognized_prefixes"] = data

    with open(output_json, 'w', encoding='utf8') as fd:
        json.dump(output_dict, fd, indent=4)
        
    for path in ["correct_dois.csv", "incorrect_dois.csv", "prefix_member_code.json", "publisher_data.csv",
                 "external_data.json"]:
        os.remove(path)

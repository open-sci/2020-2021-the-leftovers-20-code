import json
import csv

"""
In create_output() all the previously collected data are organised to be stored in the json output file. 
The aim of this function is saving the obtained results for maximizing readability and reusability of the extracted and 
computed data. 
As the first step, aoutput_dictionary is created with two keys: “citations”, whose value is a dictionary containing two 
lists (“valid” and “invalid”), and “publishers”, whose value is a list. 
Then, publisher_prefix_data dictionary is created. 
The correct_dois.csv cache file is opened and read as a DictReader object, and then iterated in a for loop. A variable 
named total_correct is created and its value is initialized to zero. For each element of the dict reader object, the value of total_correct is incremented by one and the related citation is appended to the list “valid” of the “citations” dictionary. Then, similarly, incorrect_dois.csv is opened and read as a DictReader object, and for each of its elements, the citational data is appended as a dictionary to the “invalid” list of the “citations” dictionary in the output_dict dictionary. The json file storing prefixes and publishers’ names strings as key-value pairs (i.e.: prefix_name.json) is then opened and loaded, and its key-value pairs are iterated in a for loop. In the case a value (i.e.: the string of a publisher’s name) is not a key of the dictionary publisher_prefix_data, a key-value pair is added to this latter dictionary, where the key is the publisher name and the value is a list containing the associated prefix. In the opposite case, in which the publisher’s name string is already a key in publisher_prefix_data dictionary, the prefix, which was a key in prefix_name.json, is appended to the list of prefixes associated to the publisher’s name string in publisher_prefix_data dictionary. When all data in prefix_name.json are processed, an iteration for each value of publisher_data dictionary starts: to each publisher’s dictionary is added a new key-value pair, associating to the key “prefix_list” the list that in publisher_prefix_data is associated to the string of the name of the given publisher.  The output_dict dictionary is then turned into a json file, named output.json. 
"""


def create_output(publisher_data):
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

    with open("prefix_name.json", 'r', encoding='utf8') as fd:
        data = json.load(fd)
        for key, value in data.items():
            if value not in publisher_prefix_data.keys():
                publisher_prefix_data[value] = [key]
            else:
                publisher_prefix_data[value].append(key)

    for pub in publisher_data.values():
        pub["prefix_list"] = publisher_prefix_data[pub["name"]]
        output_dict["publishers"].append(pub)

    with open("output.json", 'w', encoding='utf8') as fd:
        json.dump(output_dict, fd, indent=4)

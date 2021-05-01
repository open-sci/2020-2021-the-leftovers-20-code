import requests

"""
extract_publishers(prefix) function takes in input a prefix of a doi and returns a dictionary named “publisher”, 
containing two key value pairs, “name” and “prefix”, whose values are respectively the string of the publisher's name 
and the prefix it is identified by in the Digital Object Identifier. 
This function stores in prefix_to_name_dict information about the name and the DOI prefix of the publisher of the source 
identified by a Digital Object Identifier. 
The publisher’s data are retrieved with an API request to Crossref service for publishers data, whose response is a 
dictionary. The values associated with the keys “name” and “prefix” are stored in the locally created dictionary named 
“publisher” and then used to add a key-value pair in prefix_to_name_dict, where the keys are the publishers' prefixes 
while the values are the strings of their names. In the case in which the API request is not successful, the publisher’s 
name is classified as “unidentified”, while in the case of a connection error, an exception is risen. 
"""


def extract_publishers(prefix, prefix_to_name_dict):
    publisher = dict()
    req_url = "https://api.crossref.org/prefixes/" + prefix

    try:
        req = requests.get(url=req_url)

        req_status_code = req.status_code
        if req_status_code == 200:
            req_data = req.json()
            publisher["name"] = req_data["message"]["name"]
            publisher["prefix"] = prefix
        else:
            publisher["name"] = "unidentified"
            publisher["prefix"] = prefix

        prefix_to_name_dict[publisher["prefix"]] = publisher["name"]

    except requests.ConnectionError:
        print("failed to connect to crossref for", prefix)
        quit()

    return publisher


"""
extract_publishers_valid(row) function takes in input a two element list, which represents a citational data, obtained 
by reading the two column input csv file with the csv.reader() function and iterating it element by element, i.e. : row 
by row. The aim is managing the addition of unprocessed publisher’s dictionaries to publisher_data dictionary and the 
updating the values related to the number of either valid or invalid, addressed or received citations, in the case a 
dictionary for a given publisher already exists. 
As the first step, the prefixes of both the citing and the cited Digital Object Identifiers are extracted by splitting 
the identifiers at the separator (“/”) and storing the value of the prefixes as values of two variables, respectively 
resp_prefix and rec_prefix. 
Processing as first the DOI prefix of the citing DOI,  the existence of resp_prefix as a key in prefix_to_name_dict is 
checked, and in the affirmative case the output of extract_publishers(resp_prefix) is stored in a variable 
(responsible).Then, the string of the name of the publisher is searched among the keys in publisher_data. In the case 
the key is not yet in the dictionary, a new key-value pair is added to publisher_data, whose key is the value of “name” 
in responsible dictionary, while the value is a dictionary whose keys are “name”, “responsible_for_v”, 
“responsible_for_i”, “receiving_v”, “receiving_i”, and whose values are respectively the string of the name of the 
publisher, and the numerical values representing the number of either addressed or received, valid or invalid citational 
data. All the initial values are initialised to 0, with the exception of “responsible_for_v”, which is initialised as 1.
In the alternative case in which the string of the publisher’s name is already a key in publisher_data, the value of 
“responsible_for_v” is just incremented by one. If instead resp_prefix is already a key in prefix_to_name_dict, the only 
step to be executed is the increment by 1 of the value of the key “responsible_for_v” in the dictionary of the given 
publisher in the publisher_data dictionary. 
The very same set of actions is repeated for the rec_prefix, this time storing the output of 
extract_publishers(rec_prefix) in a variable named receiving and intervening on the value of the key "receiving_v" 
instead of that of “responsible_for_v”.
"""


def extract_publishers_valid(row, publisher_data, prefix_to_name_dict):
    resp_prefix, rec_prefix = row[0].split('/')[0], row[1].split('/')[0]

    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_name_dict)
        if responsible["name"] not in publisher_data.keys():
            publisher_data[responsible["name"]] = {
                "name": responsible["name"],
                "responsible_for_v": 1,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["name"]]["responsible_for_v"] += 1
    else:
        publisher_data[prefix_to_name_dict[resp_prefix]]["responsible_for_v"] += 1

    if rec_prefix not in prefix_to_name_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_name_dict)
        if receiving["name"] not in publisher_data.keys():
            publisher_data[receiving["name"]] = {
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 1,
                "receiving_i": 0
            }
        else:
            publisher_data[receiving["name"]]["receiving_v"] += 1
    else:
        publisher_data[prefix_to_name_dict[rec_prefix]]["receiving_v"] += 1


"""
extract_publishers_invalid(row) function performs the very same role of the above presented function 
extract_publishers_valid(row), and thus it shares this latter’s same structure. The only logical difference is that in 
the case of resp_prefix the key whose value is to be incremented is "responsible_for_i", while in the case of 
rec_prefix it is "receiving_i".
"""


def extract_publishers_invalid(row, publisher_data, prefix_to_name_dict):
    resp_prefix, rec_prefix = row[0].split('/')[0], row[1].split('/')[0]

    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_name_dict)
        if responsible["name"] not in publisher_data.keys():
            publisher_data[responsible["name"]] = {
                "name": responsible["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 1,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["name"]]["responsible_for_i"] += 1
    else:
        publisher_data[prefix_to_name_dict[resp_prefix]]["responsible_for_i"] += 1

    if rec_prefix not in prefix_to_name_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_name_dict)
        if receiving["name"] not in publisher_data.keys():
            publisher_data[receiving["name"]] = {
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 1
            }
        else:
            publisher_data[receiving["name"]]["receiving_i"] += 1
    else:
        publisher_data[prefix_to_name_dict[rec_prefix]]["receiving_i"] += 1

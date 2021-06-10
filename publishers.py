import requests
import re

"""
The publishers’ identification issue is addressed by two specular functions, 
i.e.: extract_publishers_valid(row, publisher_data, prefix_to_name_dict) and 
extract_publishers_invalid(row, publisher_data, prefix_to_name_dict), handling 
respectively data of publishers related to validated and still invalid citational 
data. Both of them call an ancillary function, i.e.: extract_publishers(prefix, 
prefix_to_name_dict), which is aimed at managing the API request to the Crossref 
API service. In particular, the used API service exploits the prefixes of the 
Digital Object Identifiers to trace back to their publishers. 
"""

"""
The function extract_publishers(prefix, prefix_to_name_dict) takes in input a prefix 
of a DOI and the dictionary prefix_to_name_dict, and it returns a dictionary named 
“publisher”, containing two key-value pairs, “name” and “prefix”, whose values are 
respectively the string of the publisher’s name and the prefix which identifies it 
in the Digital Object Identifier. Its scope is that of retrieving and storing 
information about the name and the DOI prefix of the publisher of the source 
identified by a Digital Object Identifier in the dictionary prefix_to_name_dict. 
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
            extended_member_code = req_data["message"]["member"]
            reduced_member_code = (re.findall("(\d+)", extended_member_code))[0]
            publisher["crossref_member"] = reduced_member_code
            publisher["prefix"] = prefix
        else:
            publisher["name"] = "unidentified"
            publisher["crossref_member"] = "not found"
            publisher["prefix"] = prefix

        prefix_to_name_dict[publisher["prefix"]] = (publisher["name"], publisher["crossref_member"])

    except requests.ConnectionError:
        print("failed to connect to crossref for", prefix)
        quit()
    return publisher

"""
extract_publishers_valid(row, publisher_data, prefix_to_name_dict) manages the 
addition of unprocessed publishers’ dictionaries to publisher_data and the update 
of the values related to the number of either valid or invalid addressed or received 
citations, in the case a dictionary for a given publisher already exists.
"""


def extract_publishers_valid(row, publisher_data, prefix_to_name_dict):
    resp_prefix, rec_prefix = (re.findall("(^10.\d{4,9})", row[0].split('/')[0]))[0], (re.findall("(^10.\d{4,9})", row[1].split('/')[0]))[0]
    print("this is the resp prefix", resp_prefix)
    print("this is the rec prefix", rec_prefix)



    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_name_dict)
        if responsible["crossref_member"] not in publisher_data.keys():
            publisher_data[responsible["crossref_member"]] = {
                "name": responsible["name"],
                "responsible_for_v": 1,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["crossref_member"]]["responsible_for_v"] += 1
    else:
        publisher_data[prefix_to_name_dict[resp_prefix][1]]["responsible_for_v"] += 1

    if rec_prefix not in prefix_to_name_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_name_dict)
        if receiving["crossref_member"] not in publisher_data.keys():
            publisher_data[receiving["crossref_member"]] = {
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 1,
                "receiving_i": 0
            }
        else:
            publisher_data[receiving["crossref_member"]]["receiving_v"] += 1
    else:
        publisher_data[prefix_to_name_dict[rec_prefix][1]]["receiving_v"] += 1


"""
The function extract_publishers_invalid(row, publisher_data, prefix_to_name_dict) performs 
the very same role of the above presented correspective for valid citations, and thus it 
shares this latter’s same structure. The only logical difference is that in the case of 
resp_prefix the key whose value is to be incremented is "responsible_for_i", while in 
the case of rec_prefix it is "receiving_i".
"""


def extract_publishers_invalid(row, publisher_data, prefix_to_name_dict):
    resp_prefix, rec_prefix = (re.findall("(^10.\d{4,9})", row[0].split('/')[0]))[0], (re.findall("(^10.\d{4,9})", row[1].split('/')[0]))[0]

    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_name_dict)
        if responsible["crossref_member"] not in publisher_data.keys():
            publisher_data[responsible["crossref_member"]] = {
                "name": responsible["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 1,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["crossref_member"]]["responsible_for_i"] += 1
    else:
        publisher_data[prefix_to_name_dict[resp_prefix][1]]["responsible_for_i"] += 1

    if rec_prefix not in prefix_to_name_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_name_dict)
        if receiving["crossref_member"] not in publisher_data.keys():
            publisher_data[receiving["crossref_member"]] = {
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 1
            }
        else:
            publisher_data[receiving["crossref_member"]]["receiving_i"] += 1
    else:
        publisher_data[prefix_to_name_dict[rec_prefix][1]]["receiving_i"] += 1

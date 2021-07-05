import requests
import re
from lxml import etree

"""
The publishers’ identification issue is addressed by two specular functions, 
i.e.: extract_publishers_valid(row, publisher_data, prefix_to_member_code_dict, external_data_dict) and 
extract_publishers_invalid(row, publisher_data, prefix_to_member_code_dict), handling 
respectively data of publishers related to validated and still invalid citational 
data. Both of them call an ancillary function, i.e.: extract_publishers(prefix, 
prefix_to_member_code_dict, checking=False), which is aimed at managing the API request to the Crossref 
API service. In particular, the used API service exploits the prefixes of the 
Digital Object Identifiers to trace back to their publishers. 
"""

"""
The function extract_publishers(prefix, prefix_to_member_code_dict, checking=False) takes in input a prefix 
of a DOI and the dictionary prefix_to_member_code_dict, and it returns a dictionary named 
“publisher”, containing 3 key-value pairs, “name”, "crossref_member" and “prefix”, whose values are 
respectively the string of the publisher’s name, its Crossref member code and the prefix which identifies it 
in the Digital Object Identifier. Its scope is that of retrieving and storing 
information about the name and the DOI prefix of the publisher of the source 
identified by a Digital Object Identifier in the dictionary prefix_to_member_code_dict. 
"""


def extract_publishers(prefix, prefix_to_member_code_dict, checking=False):
    if checking and prefix in prefix_to_member_code_dict.keys():
        return {"crossref_member": prefix_to_member_code_dict[prefix]}
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

        prefix_to_member_code_dict[publisher["prefix"]] = publisher["crossref_member"]

    except requests.ConnectionError:
        print("failed to connect to crossref for", prefix)
        quit()
    return publisher


def search_in_datacite(doi):
    publisher = dict()
    datacite_req_url = "https://api.datacite.org/dois/" + doi

    try:
        req = requests.get(url=datacite_req_url)

        req_status_code = req.status_code
        if req_status_code == 200:
            req_data = req.json()
            publisher["name"] = req_data["data"]["attributes"]["publisher"]
            publisher["prefix"] = doi.split('/')[0]

    except requests.ConnectionError:
        print("failed to connect to datacite for", doi)

    return publisher


def search_in_medra(doi):
    publisher = dict()
    medra_req_url = "https://api.medra.org/metadata/" + doi

    try:
        req = requests.get(url=medra_req_url)

        req_status_code = req.status_code
        if req_status_code == 200:
            tree = etree.XML(req.content)
            publisher_xpath = tree.xpath('//x:PublisherName',
                                         namespaces={'x': 'http://www.editeur.org/onix/DOIMetadata/2.0'})
            if len(publisher_xpath) == 0:
                return publisher
            publisher["name"] = publisher_xpath[0].text
            publisher["prefix"] = doi.split('/')[0]

    except requests.ConnectionError:
        print("failed to connect to crossref for", doi)

    return publisher


def search_for_cnki(doi):
    publisher = dict()
    datacite_req_url = "https://doi.org/api/handles/" + doi

    try:
        req = requests.get(url=datacite_req_url)

        req_status_code = req.status_code
        if req_status_code == 200:
            req_data = req.json()
            if 'values' in req_data.keys() and 'data' in req_data['values'][0].keys():
                if 'www.cnki.net' in req_data['values'][0]['data']['value']:
                    publisher["name"] = 'CNKI Publisher (unspecified)'
                    publisher["prefix"] = doi.split('/')[0]

    except requests.ConnectionError:
        print("failed to connect to doi for", doi)

    return publisher


def add_extra_publisher(publisher, external_data_dict, agency):
    external_data_dict[publisher['prefix']] = {
        'name': publisher['name'],
        'extracted_from': agency
    }


def search_for_publisher_in_other_agencies(doi, external_data_dict):
    publisher = search_in_datacite(doi)
    if 'name' in publisher.keys():
        add_extra_publisher(publisher, external_data_dict, 'datacite')
        return
    publisher = search_in_medra(doi)
    if 'name' in publisher.keys():
        add_extra_publisher(publisher, external_data_dict, 'medra')
        return
    publisher = search_for_cnki(doi)
    if 'name' in publisher.keys():
        add_extra_publisher(publisher, external_data_dict, 'doi')
        return


"""
extract_publishers_valid(row, publisher_data, prefix_to_member_code_dict, external_data_dict) manages the 
addition of unprocessed publishers’ dictionaries to publisher_data and the update 
of the values related to the number of either valid or invalid addressed or received 
citations, in the case a dictionary for a given publisher already exists. 
In the case a publisher's prefix doesn't allow its identification in Crossref, we call the function 
search_for_publisher_in_other_agencies(row[1], external_data_dict), in order to try to identify it in other services.
This very last option is not included for the version for not validated citations. 
"""

def extract_publishers_valid(row, publisher_data, prefix_to_member_code_dict, external_data_dict):
    resp_prefix, rec_prefix = (re.findall("(^10.\d{4,9})", row[0].split('/')[0]))[0], (re.findall("(^10.\d{4,9})", row[1].split('/')[0]))[0]

    if resp_prefix not in prefix_to_member_code_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_member_code_dict)
        if responsible["crossref_member"] not in publisher_data.keys():
            publisher_data[responsible["crossref_member"]] = {
                "crossref_member": responsible["crossref_member"],
                "name": responsible["name"],
                "responsible_for_v": 1,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["crossref_member"]]["responsible_for_v"] += 1
    else:
        publisher_data[prefix_to_member_code_dict[resp_prefix]]["responsible_for_v"] += 1

    if rec_prefix not in prefix_to_member_code_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_member_code_dict)
        if receiving["crossref_member"] not in publisher_data.keys():
            publisher_data[receiving["crossref_member"]] = {
                "crossref_member": receiving["crossref_member"],
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 1,
                "receiving_i": 0
            }
        else:
            publisher_data[receiving["crossref_member"]]["receiving_v"] += 1
    else:
        publisher_data[prefix_to_member_code_dict[rec_prefix]]["receiving_v"] += 1

    if extract_publishers(rec_prefix, prefix_to_member_code_dict, True)["crossref_member"] == "not found":
        search_for_publisher_in_other_agencies(row[1], external_data_dict)


"""
The function extract_publishers_invalid(row, publisher_data, prefix_to_member_code_dict) performs 
the very same role of the above presented corresponding function for valid citations, and thus it 
shares this latter’s same structure. The only logical difference is that in the case of 
resp_prefix the key whose value is to be incremented is "responsible_for_i", while in 
the case of rec_prefix it is "receiving_i".
"""


def extract_publishers_invalid(row, publisher_data, prefix_to_member_code_dict):
    if re.findall("(^10.\d{4,9})", row[1].split('/')[0]):
        resp_prefix, rec_prefix = (re.findall("(^10.\d{4,9})", row[0].split('/')[0]))[0], (re.findall("(^10.\d{4,9})", row[1].split('/')[0]))[0]
    else:
        print("failed to find a compliant doi prefix for the receiving doi in:", row)
        resp_prefix = (re.findall("(^10.\d{4,9})", row[0].split('/')[0]))[0]
        rec_prefix = row[1].split('/')[0]

    if resp_prefix not in prefix_to_member_code_dict.keys():
        responsible = extract_publishers(resp_prefix, prefix_to_member_code_dict)
        if responsible["crossref_member"] not in publisher_data.keys():
            publisher_data[responsible["crossref_member"]] = {
                "crossref_member": responsible["crossref_member"],
                "name": responsible["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 1,
                "receiving_v": 0,
                "receiving_i": 0
            }
        else:
            publisher_data[responsible["crossref_member"]]["responsible_for_i"] += 1
    else:
        publisher_data[prefix_to_member_code_dict[resp_prefix]]["responsible_for_i"] += 1

    if rec_prefix not in prefix_to_member_code_dict.keys():
        receiving = extract_publishers(rec_prefix, prefix_to_member_code_dict)
        if receiving["crossref_member"] not in publisher_data.keys():
            publisher_data[receiving["crossref_member"]] = {
                "crossref_member": receiving["crossref_member"],
                "name": receiving["name"],
                "responsible_for_v": 0,
                "responsible_for_i": 0,
                "receiving_v": 0,
                "receiving_i": 1
            }
        else:
            publisher_data[receiving["crossref_member"]]["receiving_i"] += 1
    else:
        publisher_data[prefix_to_member_code_dict[rec_prefix]]["receiving_i"] += 1

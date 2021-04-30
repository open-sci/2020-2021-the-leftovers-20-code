import requests
import json
import csv
import os
from itertools import islice


def extract_publishers(prefix):
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


def extract_publishers_valid(row):
    resp_prefix, rec_prefix = row[0].split('/')[0], row[1].split('/')[0]

    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix)
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
        receiving = extract_publishers(rec_prefix)
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


def extract_publishers_invalid(row):
    resp_prefix, rec_prefix = row[0].split('/')[0], row[1].split('/')[0]

    if resp_prefix not in prefix_to_name_dict.keys():
        responsible = extract_publishers(resp_prefix)
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
        receiving = extract_publishers(rec_prefix)
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


def write_to_csv():
    global correct_dois_data, incorrect_dois_data
    if not os.path.exists('correct_dois.csv'):
        with open('correct_dois.csv', 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Valid_cited_doi'])

    if not os.path.exists('incorrect_dois.csv'):
        with open('incorrect_dois.csv', 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Invalid_cited_doi'])

    with open('correct_dois.csv', 'a') as fd:
        writer = csv.writer(fd)
        writer.writerows(correct_dois_data)
        correct_dois_data = []

    with open('incorrect_dois.csv', 'a') as fd:
        writer = csv.writer(fd)
        writer.writerows(incorrect_dois_data)
        incorrect_dois_data = []

    with open('publisher_data.csv', 'w') as fd:
        dict_writer = csv.DictWriter(fd, ['name', 'responsible_for_v', 'responsible_for_i', 'receiving_v',
                                          'receiving_i'])
        dict_writer.writeheader()
        dict_writer.writerows(publisher_data.values())

    with open('prefix_name.json', 'w', encoding='utf-8') as fd:
        json.dump(prefix_to_name_dict, fd, ensure_ascii=False, indent=4)


def extract_row_number():
    global prefix_to_name_dict
    num = 0
    if not os.path.exists('publisher_data.csv'):
        return num
    else:
        with open('publisher_data.csv', 'r') as read_obj:
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

        with open("prefix_name.json", 'r') as fd:
            prefix_to_name_dict = json.load(fd)

        return num


def create_output():
    output_dict = {
        "citations": {
            "valid": list(),
            "invalid": list()
        },
        "publishers": list()
    }
    publisher_prefix_data = dict()

    with open("correct_dois.csv", 'r') as fd:
        total_correct = 0
        reader = csv.DictReader(fd)
        for row in reader:
            output_dict["citations"]["valid"].append(dict(row))
            total_correct += 1
        output_dict["total_num_of_valid_citations"] = total_correct

    with open("incorrect_dois.csv", 'r') as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            output_dict["citations"]["invalid"].append(dict(row))

    with open("prefix_name.json", 'r') as fd:
        data = json.load(fd)
        for key, value in data.items():
            if value not in publisher_prefix_data.keys():
                publisher_prefix_data[value] = [key]
            else:
                publisher_prefix_data[value].append(key)

    for pub in publisher_data.values():
        pub["prefix_list"] = publisher_prefix_data[pub["name"]]
        output_dict["publishers"].append(pub)

    with open("output.json", 'w') as fd:
        json.dump(output_dict, fd, indent=4)


with open('invalid_doi_part.csv', 'r') as read_obj:
    publisher_data = dict()
    prefix_to_name_dict = dict()
    correct_dois_data = []
    incorrect_dois_data = []
    start_index = extract_row_number()
    csv_reader = csv.reader(islice(read_obj, start_index+1, None))

    i = 0
    for row in csv_reader:
        if i == 100:
            write_to_csv()
            print("So far processed", start_index+i, "rows.")
            start_index = start_index + i
            i = 0
        URL = "https://doi.org/api/handles/" + row[1]
        try:
            r = requests.get(url=URL)
            status_code = r.status_code
            if status_code == 200:
                correct_dois_data.append(row)
                extract_publishers_valid(row)
            else:
                incorrect_dois_data.append(row)
                extract_publishers_invalid(row)
        except requests.ConnectionError:
            print("failed to connect to doi for row", row)
            quit()

        i += 1
    write_to_csv()
    create_output()

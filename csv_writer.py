import json
import csv
import os

"""
This part of the code is aimed at limiting the possibility of losing the already processed data, 
in the case some problem occurs during the code run.  As the first step, the existence in the 
local directory of “correct_dois.csv” and “incorrect_dois.csv” files is verified. In the case 
the aforementioned files do not exist, they are then created, and their first row is filled with 
the headers of the two columns, i.e.: 'Valid_citing_doi' and 'Invalid_cited_doi'. The two CSV 
files are then opened and respectively compiled by using the data stored in correct_dois_data 
and incorrect_dois_data. The following step implies opening in write mode the 
“publisher_data.csv” file and assigning the following headers: 'name', 'responsible_for_v', 
'responsible_for_i', 'receiving_v', 'receiving_i'. The rows are then filled with the data 
derived from the publisher_data dictionary.  Eventually, “prefix_member_code.json” and 'external_data.json' 
files are opened  in write mode and accordingly filled with prefix_to_member_code_dict values. 

"""


def write_to_csv(publisher_data, prefix_to_member_code_dict, external_data_dict, correct_dois_data, incorrect_dois_data):
    if not os.path.exists('correct_dois.csv'):
        with open('correct_dois.csv', 'w', encoding='utf8') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Valid_cited_doi', "Validation_time"])

    if not os.path.exists('incorrect_dois.csv'):
        with open('incorrect_dois.csv', 'w', encoding='utf8') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Invalid_cited_doi', "Validation_time"])

    with open('correct_dois.csv', 'a', encoding='utf8') as fd:
        writer = csv.writer(fd)
        writer.writerows(correct_dois_data)

    with open('incorrect_dois.csv', 'a', encoding='utf8') as fd:
        writer = csv.writer(fd)
        writer.writerows(incorrect_dois_data)

    with open('publisher_data.csv', 'w', encoding='utf8') as fd:
        dict_writer = csv.DictWriter(fd, ['crossref_member', 'name', 'responsible_for_v', 'responsible_for_i',
                                          'receiving_v',
                                          'receiving_i'])
        dict_writer.writeheader()
        dict_writer.writerows(publisher_data.values())

    with open('prefix_member_code.json', 'w', encoding='utf-8') as fd:
        json.dump(prefix_to_member_code_dict, fd, ensure_ascii=False, indent=4)

    with open('external_data.json', 'w', encoding='utf-8') as fd:
        json.dump(external_data_dict, fd, ensure_ascii=False, indent=4)

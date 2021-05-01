import json
import csv
import os

"""
write_to_csv function is focused on the creation of the ancillary csv files where the intermediate results obtained are temporarily saved, in order to limitate the possibility of losing the already processed data, in the case some problem occurs during the code run.  As the first step, the existence in the local directory of “correct_dois.csv” and “incorrect_dois.csv” files is verified. In the case the aforementioned files do not exist, they are then created, and their first row is filled with the names of the two columns, i.e.: 'Valid_citing_doi' and 'Invalid_cited_doi'. The two CSV files are then opened and respectively compiled by using the data stored respectively in correct_dois_data and incorrect_dois_data. At this point, the two lists correct_dois_data and incorrect_dois_data are emptied.  The following step implies opening in write mode publisher_data.csv, assigning the following headers: 'name', 'responsible_for_v', 'responsible_for_i', 'receiving_v', 'receiving_i', and filling the rows with the data derived from the publisher_data dictionary.  Eventually, “prefix_name.json” file is opened in write mode, and it is filled with prefix_to_name_dict values. 
"""


def write_to_csv(publisher_data, prefix_to_name_dict, correct_dois_data, incorrect_dois_data):
    if not os.path.exists('correct_dois.csv'):
        with open('correct_dois.csv', 'w', encoding='utf8') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Valid_cited_doi'])

    if not os.path.exists('incorrect_dois.csv'):
        with open('incorrect_dois.csv', 'w', encoding='utf8') as fd:
            writer = csv.writer(fd)
            writer.writerow(['Valid_citing_doi', 'Invalid_cited_doi'])

    with open('correct_dois.csv', 'a', encoding='utf8') as fd:
        writer = csv.writer(fd)
        writer.writerows(correct_dois_data)

    with open('incorrect_dois.csv', 'a', encoding='utf8') as fd:
        writer = csv.writer(fd)
        writer.writerows(incorrect_dois_data)

    with open('publisher_data.csv', 'w', encoding='utf8') as fd:
        dict_writer = csv.DictWriter(fd, ['name', 'responsible_for_v', 'responsible_for_i', 'receiving_v',
                                          'receiving_i'])
        dict_writer.writeheader()
        dict_writer.writerows(publisher_data.values())

    with open('prefix_name.json', 'w', encoding='utf-8') as fd:
        json.dump(prefix_to_name_dict, fd, ensure_ascii=False, indent=4)

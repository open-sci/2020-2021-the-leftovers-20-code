import requests
import csv
from itertools import islice
from row_number_extractor import extract_row_number
from csv_writer import write_to_csv
from publishers import extract_publishers_valid, extract_publishers_invalid
from output_creator import create_output

"""
The input csv file is opened in “read” modality. Then, two dictionaries and two lists are created.
Here are listed their functions and organization: 

1) publisher_data: This structure is projected to be a dictionary whose keys are the strings of the publishers’ names, 
while the values are other dictionaries storing information about each publisher. In detail, each publisher’s dictionary 
contains the following key-value pairs: "name": whose value is the string of the publisher’s name, "responsible_for_v": 
whose value is an integer number representing the number of  validated citational data of which the publisher is 
responsible for, "responsible_for_i": whose value is an integer number representing the number of  still invalid 
citational data of which the publisher is responsible for, "receiving_v": whose value is an integer number representing 
the number of validated citational data where the publisher is associated with the referenced DOI, "receiving_i": whose 
value is an integer number representing the number of  still invalid citational data where the publisher is associated 
with the referenced DOI, “prefix_list” : whose value is a list containing the prefixes associated with the publisher.
 
2) prefix_to_name_dict: This structure’s function is that of storing as key-value pairs prefixes and strings of the 
names of the publishers. The focus of this dictionary is providing a locally-stored mapping of all the prefixes already 
processed, in order to avoid redundant API requests to identify publishers.

3) correct_dois_data: This list is meant to store validated citational data as dictionaries containing two key-value 
pairs, one representing the citing DOI and the other representing the referenced DOI. 

4) incorrect_dois_data: This list shares the very same role of correct_dois_data, but for citational data which could 
not be validated during the process, which are thus still invalid.
 
Since the main process is structured as a for loop, a start index (start_index) is identified through a function 
allowing the count of the already processed citational data, so that only the remaining slice of the original file can 
be read and processed. As a security guarantee in a long process of execution, each hundred rows of the input csv file 
processed, the results are saved in the cache files.
In this for loop, for each row processed, the validity of the receiving Digital Object Identifier is checked through an 
API request. In the case the request is successful, the citational data is appended to correct_dois_data and the 
publishers identification proceeds with the execution of the extract_publishers_valid(row) function; otherwise, the 
citational data is appended to incorrect_dois_data list and the publishers’ identification is managed with 
extract_publishers_invalid(row).
 
In case of a connection error, an exception is risen. 
Once all the lines of the original input file have been processed, the write_to_csv() function for cache files 
compilation is called again, and the function to create the output file is executed. 
"""

if __name__ == '__main__':
    with open('invalid_dois.csv', 'r', encoding='utf8') as read_obj:
        publisher_data = dict()
        correct_dois_data = []
        incorrect_dois_data = []
        start_index, prefix_to_name_dict = extract_row_number(publisher_data)
        csv_reader = csv.reader(islice(read_obj, start_index + 1, None))

        i = 0
        for row in csv_reader:
            if i == 100:
                write_to_csv(publisher_data, prefix_to_name_dict, correct_dois_data, incorrect_dois_data)
                correct_dois_data = []
                incorrect_dois_data = []
                print("So far processed", start_index + i, "rows.")
                start_index = start_index + i
                i = 0
            URL = "https://doi.org/api/handles/" + row[1]
            try:
                r = requests.get(url=URL)
                status_code = r.status_code
                if status_code == 200:
                    correct_dois_data.append(row)
                    extract_publishers_valid(row, publisher_data, prefix_to_name_dict)
                else:
                    incorrect_dois_data.append(row)
                    extract_publishers_invalid(row, publisher_data, prefix_to_name_dict)
            except requests.ConnectionError:
                print("failed to connect to doi for row", row)
                quit()

            i += 1
        write_to_csv(publisher_data, prefix_to_name_dict, correct_dois_data, incorrect_dois_data)
        correct_dois_data = []
        incorrect_dois_data = []
        create_output(publisher_data)

import requests
import csv
from itertools import islice
from row_number_extractor import extract_row_number
from csv_writer import write_to_csv
from publishers import extract_publishers_valid, extract_publishers_invalid
from output_creator import create_output
from datetime import datetime

"""
The input csv file is opened and the following data structures are created: 
1) publisher_data dictionary, aimed at storing dictionaries representing each publisher encountered;
2) correct_dois_data list, aimed at storing citational data validated throughout the process;
3) incorrect_dois_data list, aimed at storing citational data which could not be validated.

Then, two variables (i.e. : start_index and prefix_to_name_dict) are assigned the values 
returned by the function extract_row_number(publisher_data), aimed at keeping track of 
the lines of input material already processed. A recovery mechanism based on the creation 
of ancillary files provides the possibility to overcome potential interruptions of the 
process by restarting the code run from the last line of the input csv file whose data 
was successfully retrieved. 

Accordingly, the software can work on a sliced amount of the input material. 
The input file is read with a csv reader and iterated row by row. 
In this for loop, for each row processed, the validity of the receiving Digital Object 
Identifier is checked through an API request. In the case the request is successful, 
the citational data is appended to the list of validated citations (i.e.: correct_dois_data), 
and the publisher identification for both citing and cited doi proceeds with the execution 
of extract_publishers_valid(row, publisher_data, prefix_to_name_dict). 
Otherwise, the citational data is appended to the incorrect_dois_data list and the 
publishers’ identification is managed with the correspective function for invalid 
citational data, i.e.: extract_publishers_invalid(row, publisher_data, prefix_to_name_dict). 
In case of a connection error, an exception is raised. 

Every hundred lines processed, the function write_to_csv(publisher_data, prefix_to_name_dict, 
correct_dois_data, incorrect_dois_data) is executed and the lists correct_dois_data and 
incorrect_dois_data are emptied, so as to save the processed material in files conceived for this purpose.
Once all the lines of the original input file have been processed, the write_to_csv(publisher_data, 
prefix_to_name_dict, correct_dois_data, incorrect_dois_data) function for cache files compilation 
is called for the last time, and then the function to create the output file is executed. 

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
                    validation_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    row.append(validation_time)
                    correct_dois_data.append(row)
                    extract_publishers_valid(row, publisher_data, prefix_to_name_dict)
                else:
                    validation_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    row.append(validation_time)
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

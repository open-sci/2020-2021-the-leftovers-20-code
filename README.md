# Investigating Missing Citations in COCI and the Publishers Involved

In this repository you can find all the code used for our course project for the Open Science course in the academic year 2020-2021. The main purpose of this project has been to extract the publishers involved in providing invalid citation data to Crossref and the publishers whose articles receive such invalid citations. We have used a [dataset](https://doi.org/10.5281/zenodo.4625300) created by the creators of [COCI](https://opencitations.net/index/coci) while extracting data from Crossref.

You can read a more in-depth description of our project in the [related article](https://doi.org/10.5281/zenodo.4735635) and see our results visualized in our [Github Pages website](https://open-sci.github.io/2020-2021-the-leftovers-20-code/index.html). The final output resulted from executing this code on our source dataset can be found [here]().

## How to Run the Code

In order to avoid errors, make sure you have a version of Python 3 installed and have the lxml package on it. Here's the command that runs the code:
```
$ python invalid_dois.py <input_csv_address> <output_json_address> <checkpoint_threshold>
```
The first argument is the address to the CSV dataset you want to investigate and the second argument is the address to the desired output JSON file. Both must include the extension. The third argument represents the number of lines to read from the input file before saving the results to the cache files. You can stop the execution at any time and rerun it at a later time without losing the data processed up to that point thanks to the cache files created during the process.

## Hardware Configuration

The entire execution of the code took place on a computer with the following relevant hardware specifications:

- CPU: Intel Core i7
- RAM: 8.00 GB
- Storage: 2 TB HDD

## See Also

- [Our Article](https://doi.org/10.5281/zenodo.4735635)
- [Our Website](https://open-sci.github.io/2020-2021-the-leftovers-20-code/index.html)
- [Our Protocol](10.17504/protocols.io.buqhnvt6)
- [Our Data Management Plan](10.5281/zenodo.4671486)
- [Our Result Dataset]()
- [Our Source Dataset](https://doi.org/10.5281/zenodo.4625300)
- [Our Sister Project](https://github.com/open-sci/2020-2021-grasshoppers-code)
- [COCI](https://opencitations.net/index/coci)

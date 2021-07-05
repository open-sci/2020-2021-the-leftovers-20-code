import unittest
from row_number_extractor import extract_row_number
from csv_writer import write_to_csv
from publishers import extract_publishers_valid, extract_publishers_invalid, extract_publishers
from output_creator import create_output
from invalid_dois import invalid_dois_main
import os.path


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.test_publisher_data = {
            '5777': {
                'crossref_member': '5777',
                'name': 'VLDB Endowment',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '7822': {
                'crossref_member': '7822',
                'name': 'Test accounts',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 2
            },
            '3673': {
                'crossref_member': '3673',
                'name': 'University of Illinois Press',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '1121': {
                'crossref_member': '1121',
                'name': 'JSTOR',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 1
            },
            '276': {
                'crossref_member': '276',
                'name': 'Ovid Technologies (Wolters Kluwer Health)',
                'responsible_for_v': 0,
                'responsible_for_i': 3,
                'receiving_v': 0,
                'receiving_i': 3
            },
            '179': {
                'crossref_member': '179',
                'name': 'SAGE Publications',
                'responsible_for_v': 0,
                'responsible_for_i': 2,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '2060': {
                'crossref_member': '2060',
                'name': 'Baishideng Publishing Group Inc.',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 1
            },
            '301': {
                'crossref_member': '301',
                'name': 'Informa UK Limited',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '266': {
                'crossref_member': '266',
                'name': 'IOP Publishing',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 1
            },
            '311': {
                'crossref_member': '311',
                'name': 'Wiley',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 2
            },
            '98': {
                'crossref_member': '98',
                'name': 'Hindawi Limited',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            'not found': {
                'crossref_member': 'not found',
                'name': 'unidentified',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 1,
                'receiving_i': 1
            },
            '2432': {
                'crossref_member': '2432',
                'name': 'IGI Global',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '320': {
                'crossref_member': '320',
                'name': 'Association for Computing Machinery (ACM)',
                'responsible_for_v': 0,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '297': {
                'crossref_member': '297',
                'name': 'Springer Science and Business Media LLC',
                'responsible_for_v': 1,
                'responsible_for_i': 1,
                'receiving_v': 0,
                'receiving_i': 0
            },
            '1968': {
                'crossref_member': '1968',
                'name': 'MDPI AG',
                'responsible_for_v': 0,
                'responsible_for_i': 0,
                'receiving_v': 0,
                'receiving_i': 1
            }
        }

        self.test_prefix_to_member_code_dict = {'10.14778': '5777',
                                         '10.5555': '7822',
                                         '10.5406': '3673',
                                         '10.2307': '1121',
                                         '10.1161': '276',
                                         '10.1177': '179',
                                         '10.3748': '2060',
                                         '10.1080': '301',
                                         '10.1070': '266',
                                         '10.1111': '311',
                                         '10.1155': '98',
                                         '10.3760': 'not found',
                                         '10.4018': '2432',
                                         '10.1002': '311',
                                         '10.1145': '320',
                                         '10.1007': '297',
                                         '10.3390': '1968',
                                         '10.13745': 'not found'}

        self.test_correct_dois_data = [
            ['10.1007/s11771-020-4410-2', '10.13745/j.esf.2016.02.011', '05/31/2021, 20:46:16']]
        self.test_incorrect_dois_data = [['10.14778/1920841.1920954', '10.5555/646836.708343', '05/31/2021, 20:46:03'],
                                         ['10.5406/ethnomusicology.59.2.0202', '10.2307/20184517',
                                          '05/31/2021, 20:46:04'],
                                         ['10.1161/01.cir.63.6.1391', '10.1161/circ.37.4.509', '05/31/2021, 20:46:05'],
                                         ['10.1177/1179546820918903', '10.3748/wjg.v10.i5.707.',
                                          '05/31/2021, 20:46:06'],
                                         ['10.1080/10410236.2020.1731937', '10.1070/10810730903528033',
                                          '05/31/2021, 20:46:08'],
                                         ['10.1161/strokeaha.112.652065', '10.1161/str.24.7.8322400',
                                          '05/31/2021, 20:46:09'],
                                         ['10.1177/1049732310393747', '10.1111/j.545-5300.2003.42208.x',
                                          '05/31/2021, 20:46:09'],
                                         ['10.1155/2017/1491405', '10.3760/cma.j.issn.0366-6999.20131202',
                                          '05/31/2021, 20:46:10'],
                                         ['10.1161/01.res.68.6.1549', '10.1161/res.35.2.159', '05/31/2021, 20:46:12'],
                                         ['10.4018/978-1-5225-2650-6.ch006', '10.1002/per', '05/31/2021, 20:46:12'],
                                         ['10.1145/2525314.2594229', '10.5555/1873601.1873616', '05/31/2021, 20:46:13'],
                                         ['10.1007/s10619-020-07320-z',
                                          '10.3390/sym11070911www.mdpi.com/journal/symmetry', '05/31/2021, 20:46:14']]

        self.test_external_data_dict= {'10.13745': {'name': 'CNKI Publisher (unspecified)', 'extracted_from': 'doi'}}
        self.correct_dois_csv_filepath = "correct_dois.csv"
        self.incorrect_dois_csv_filepath = "incorrect_dois.csv"
        self.prefix_member_code_json_filepath = "prefix_member_code.json"
        self.publisher_data_csv_filepath = "publisher_data.csv"
        self.output_json_filepath = "output.json"
        self.valid_doi_prefix = "10.1007"
        self.invalid_doi_prefix = "10.5555"
        self.validated_cit_row = ['10.1007/s11771-020-4410-2', '10.13745/j.esf.2016.02.011', '05/31/2021, 20:29:31']
        self.validated_cit_row_citing = "297" #'Springer Science and Business Media LLC'
        self.validated_cit_row_cited = "not found" #'unidentified'
        self.invalid_cit_row = ['10.14778/1920841.1920954', '10.5555/646836.708343', '05/31/2021, 20:29:18']
        self.invalid_cit_row_citing = "5777" #'VLDB Endowment'
        self.invalid_cit_row_cited = "7822" #'Test accounts'
        self.example_output_path= "ex_output.json"
        self.example_output_path_2= "ex_output_2.json"
        self.example_input_path= "ex_input.csv"

    def test_invalid_dois_main(self):
        invalid_dois_main(2, self.example_input_path, self.example_output_path)
        self.assertTrue(os.path.isfile(self.example_output_path))

    def test_write_to_csv_and_extract_row_number_and_create_output(self):
        write_to_csv( self.test_publisher_data, self.test_prefix_to_member_code_dict, self.test_external_data_dict, 
                      self.test_correct_dois_data,
                      self.test_incorrect_dois_data )
        self.assertTrue( os.path.isfile( self.correct_dois_csv_filepath ) )
        self.assertTrue( os.path.isfile( self.incorrect_dois_csv_filepath ) )
        self.assertTrue( os.path.isfile( self.prefix_member_code_json_filepath ) )
        self.assertTrue( os.path.isfile( self.publisher_data_csv_filepath ) )
        self.assertEqual(extract_row_number( self.test_publisher_data ), (13, self.test_prefix_to_member_code_dict, 
                                                                          self.test_external_data_dict))
        create_output( self.test_publisher_data, self.example_output_path_2)
        self.assertTrue( os.path.isfile( self.output_json_filepath ) )
        self.assertFalse( os.path.isfile( self.correct_dois_csv_filepath ) )
        self.assertFalse( os.path.isfile( self.incorrect_dois_csv_filepath ) )
        self.assertFalse( os.path.isfile( self.prefix_member_code_json_filepath ) )
        self.assertFalse( os.path.isfile( self.publisher_data_csv_filepath ) )


    def test_extract_publishers_valid(self):
        extract_publishers_valid( self.validated_cit_row, self.test_publisher_data, self.test_prefix_to_member_code_dict, self.test_external_data_dict)
        self.assertIn(self.validated_cit_row_citing, self.test_publisher_data.keys() )
        self.assertIn( self.validated_cit_row_cited, self.test_publisher_data.keys() )
        self.assertTrue( self.test_publisher_data[self.validated_cit_row_citing]['responsible_for_v'] >= 1 )
        self.assertTrue( self.test_publisher_data[self.validated_cit_row_cited]['receiving_v'] >= 1 )

    def test_extract_publishers_invalid(self):
        extract_publishers_invalid( self.invalid_cit_row, self.test_publisher_data, self.test_prefix_to_member_code_dict )
        self.assertIn( self.invalid_cit_row_citing, self.test_publisher_data.keys() )
        self.assertIn( self.invalid_cit_row_cited, self.test_publisher_data.keys() )
        self.assertTrue( self.test_publisher_data[self.invalid_cit_row_citing]['responsible_for_i'] >= 1 )
        self.assertTrue( self.test_publisher_data[self.invalid_cit_row_cited]['receiving_i'] >= 1 )

    def test_extract_publishers(self):
        self.assertEqual( extract_publishers( self.invalid_doi_prefix, self.test_prefix_to_member_code_dict ),
                          {'crossref_member': '7822', 'name': 'Test accounts', 'prefix': '10.5555'})
        self.assertEqual( extract_publishers( self.valid_doi_prefix, self.test_prefix_to_member_code_dict ),
                          {'crossref_member': '297', 'name': 'Springer Science and Business Media LLC', 'prefix': '10.1007'} )


if __name__ == '__main__':
    unittest.main()

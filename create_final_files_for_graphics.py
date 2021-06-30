import json
import csv


def create_files():
    with open('final_output.json', 'r') as jsonfile:
        initial_data = json.load(jsonfile)
        # creating data structures
        l_20_citing = []
        l_20_cited = []
        l_10_citing = []
        l_10_cited = []
        # richiamiamo la funzione ancillare per riempire le liste di dizionari
        l_20_citing = fill_and_order(initial_data, l_20_citing, 'responsible_for_v', 'responsible_for_i', 'citing')
        l_20_cited = fill_and_order(initial_data, l_20_cited, 'receiving_v', 'receiving_i', 'cited')
        l_10_citing = fill_list_of_10(l_20_citing, l_10_citing, 'responsible_for_v', 'responsible_for_i')
        l_10_cited = fill_list_of_10(l_20_cited, l_10_cited, 'receiving_v', 'receiving_i')

        print('lista dei 10 citanti: ', l_10_citing)
        print('lista dei 10 citati: ', l_10_cited)

        # decifrazione doppioni nei citati (Ovid-Virgilio)
        decode_to_json = []
        names_to_reverse = []
        color = ['#E0851D', '#EDA713', '#F9C909', '#738C40', '#60B482', '#4CDCC4', '#432F9B', '#D230BF', '#D52E85', '#D82C4B']
        clr_idx = -1
        for citing_dict in l_10_citing:
            clr_idx += 1
            for cited_dict in l_10_cited:
                if citing_dict['name'] == cited_dict['name']:
                    names_to_reverse.append(citing_dict['name'])
                    cur_node=[{
                        'id': citing_dict['name'][::-1],
                        'name': citing_dict['name'],
                        'color': color[clr_idx]
                    },
                    {
                        'id': citing_dict['name'],
                        'name': citing_dict['name'],
                        'color': color[clr_idx]
                    }]
                    for node in cur_node:
                        decode_to_json.append(node)
                    break
        print('Lista dei nomi da convertire alla fine della funzione: ', names_to_reverse)
        print('Lista con i dizionari per la decodifica: ', decode_to_json)

        # chi citano i citanti
        list_to_json = []

        for dct in l_10_citing:
            for prefix in dct['prefix_list'].split('__'):
                list_to_json = cit_iteration(initial_data, prefix, l_10_cited, dct['name'], list_to_json, 'valid')
                list_to_json = cit_iteration(initial_data, prefix, l_10_cited, dct['name'], list_to_json, 'invalid')

        # conversione degli id di from secondo la lista names_to_reverse
        for dct in list_to_json:
            for name in names_to_reverse:
                if dct['from'] == name:
                    dct['from'] = dct['from'][::-1]
                    break
        final_graph = {'links': list_to_json, 'decode': decode_to_json}

    with open('links_decode.json', 'w', encoding='utf8') as jsn:
        json.dump(final_graph, jsn, indent=4)
    with open('decode.json', 'w', encoding='utf8') as jsn:
        json.dump(decode_to_json, jsn, indent=4)
        with open('links.json', 'w', encoding='utf8') as jsn_file:
            json.dump(list_to_json, jsn_file, indent=4)

    print('Lista con i dizionari dei collegamenti da convertire in JSON: ', list_to_json)


def cit_iteration(initial_data, prefix, l_10_cited, dct_name, list_to_json, status):

    for valid_cit in initial_data['citations'][status]:
        if prefix + '/' in valid_cit['Valid_citing_doi']:
            prefix_match=False
            n = 0
            while n<len(l_10_cited):
                m = 0
                cur_prefix_list = l_10_cited[n]['prefix_list'].split('__')
                while m<len(cur_prefix_list):
                    if cur_prefix_list[m] == valid_cit[status.capitalize()+'_cited_doi'].split('/')[0]:
                        list_to_json = pop_json_dict(list_to_json, dct_name, l_10_cited[n]['name'])
                        n = len(l_10_cited)
                        m = len(cur_prefix_list)
                        prefix_match=True
                    else:
                        m += 1
                n += 1
            if not prefix_match:
                list_to_json = pop_json_dict(list_to_json, dct_name, 'other')
    return list_to_json

'''
def manage_double_forloop (l_10_cited):
    for cited_dict in l_10_cited:
        for cited_prefix in cited_dict['prefix_list'].split('__'):
            yield cited_dict, cited_prefix
'''


def pop_json_dict(list_to_json, dct_name, to_name):
    found = False
    if len(list_to_json) > 0:
        for listed_dict in list_to_json:
            if listed_dict['from']== dct_name and listed_dict['to']==to_name:
                listed_dict['weight']+=1
                found=True
    # il dizionario va creato sia se non esiste già il match from-to, sia se la lista è vuota e non serve iterare
    if len(list_to_json) == 0 or not found:
        cur_dict = {
            'from': dct_name,
            'to': to_name,
            'weight': 1
        }
        list_to_json.append(cur_dict)

    return list_to_json


def fill_and_order(initial_data, list_name, num_valid, num_invalid, name_for_csv):
    all_pub_data = []

    for p in initial_data['publishers']:
        new_p = {
            'name': p['name'],
            'responsible_for_v': p['responsible_for_v'],
            'responsible_for_i': p['responsible_for_i'],
            'receiving_v': p['receiving_v'],
            'receiving_i': p['receiving_i'],
            'prefix_list': p['prefix_list']
        }

        all_pub_data.append(new_p)


        joined_ids = '__'.join(new_p['prefix_list'])
        new_p['prefix_list'] = joined_ids

        if len(list_name) <= 19:
            list_name.append(new_p)
        else:
            pos = 0
            smallest_value = list_name[0][num_valid]+list_name[0][num_invalid]
            for d in list_name:
                if d[num_valid]+d[num_invalid] < smallest_value:
                    smallest_value = d[num_valid]+d[num_invalid]
                    pos = list_name.index(d)
            if new_p[num_valid]+new_p[num_invalid] > smallest_value:
                list_name[pos] = new_p

        list_name.sort(reverse=True, key=lambda x: x[num_valid]+x[num_invalid])

    #mettere all_pub_data su un csv per le tabelle dopo aver ordinato i dizionari in ordine alfabetico
    new_all_pub_data = sorted(all_pub_data, key=lambda k: k['name'])
    with open('all_pub_data_for_tables.csv', 'w', encoding='utf8', newline='') as csvfile:
        fieldnames = new_all_pub_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in new_all_pub_data:
            writer.writerow(row)

    # QUANDO ARRIVA IL FILE FINALE LEVARE IL COMMENTO PER CREARE I NUOVI CSV
    with open(name_for_csv + '_bar_chart.csv', mode='w', encoding='utf8') as my_file:
        my_writer=csv.DictWriter(my_file, list_name[0].keys())
        my_writer.writeheader()
        my_writer.writerows(list_name)

    return list_name


def fill_list_of_10(name_l_of_20, name_l_of_10, num_valid, num_invalid):
    idx = 0
    while idx < 10:  # in realtà saranno 10
        cur_dict=name_l_of_20[idx]
        name_l_of_10.append({
            'name': cur_dict['name'],
            'tot': cur_dict[num_valid]+cur_dict[num_invalid],
            'prefix_list': cur_dict['prefix_list']
        })
        idx += 1
    return name_l_of_10


def question_three():
    with open("final_output.json", errors='ignore', encoding='utf-8') as inputjson:
        data = json.load(inputjson)

        new_data = {'total_num_of_invalid_citations': len(data["citations"]["invalid"]),
                    'total_num_of_valid_citations': data['total_num_of_valid_citations']}

    with open('q3.json', 'w', encoding='utf-8') as outfile:
        json.dump(new_data, outfile, indent=2)


question_three()

create_files()


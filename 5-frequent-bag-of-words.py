from collections import OrderedDict
import numpy as np
import re
import json
import os
import csv

companies = [
	"maybank",
	"axiata",
	"cimb",
	"petronas"
]

labels = [
	"positive",
	"negative",
]

directories = [
	"data/bag-of-words/positive",
	"data/bag-of-words/negative"
]

def check_combination_word_exist(article, word):
    result = False
    article_words = article.split()
    for article_word in article_words:
        if (article_word == word):
            result = True

    return result

for company in companies:
    article_filename = company.replace(" ", "-") + "-data.json"
    csv_filename = company.replace(" ", "-") + "-data.csv"
    itemset_csv = company.replace(" ", "-") + '-frequent-itemset.csv'
    for label in labels:
		# create directory
        for directory in directories:
			if not os.path.exists(directory):
				os.makedirs(directory)

        # new file
        bags_csv = open('data/bag-of-words/' + label + '/' + csv_filename, "w")

        # open article
        with open('data/labelled/' + label + '/' + article_filename) as article_file:
            # open frequent-itemset
            item_set = open('data/frequent-itemset/' + label + '/' + itemset_csv)
            reader = csv.reader(item_set, delimiter=',')

            # create header
            header = 'articles,'
            for frequent_itemset_row in reader:
                header = header + ",".join(frequent_itemset_row) + "\n"
                bags_csv.write(header)

            # load article
            labelled_data = json.load(article_file, object_pairs_hook=OrderedDict)
            for key_json, value_json in labelled_data.items():
                data = key_json + ','
                item_set = open('data/frequent-itemset/' + label + '/' + itemset_csv)
                reader = csv.reader(item_set, delimiter=',')
                for frequent_itemset_rows in reader:
                    for frequent_itemset_column in frequent_itemset_row:
                        value = 1
                        for word in frequent_itemset_column.split():
                            result = check_combination_word_exist(value_json['article'], word)
                            if (result != True):
                                value = 0
                                break;

                        print(company + ' | ' + label + ' | article ' + key_json + ' | ' + frequent_itemset_column + ' -> ' + str(value))
                        data = data + str(value) + ','
                bags_csv.write(data[:-1] + "\n")

            bags_csv.close
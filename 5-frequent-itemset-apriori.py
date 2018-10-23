import numpy as np
import pandas as pd
import re
import json
import os
from colors import bcolors
from apriori.transactionencoder import TransactionEncoder
from apriori.apriori import apriori

companies = [
	# "maybank",
	#"axiata",
	# "cimb",
	# "petronas",
	# "sime darby"
	"testing"
]

labels = [
	# "positive",
	"negative",
	# "neutral"
]

directories = [
	"data/apriori/positive",
	"data/apriori/negative",
	"data/apriori/neutral"
]

def tokenize_sentences(sentences):
    words = []
    for sentence in sentences:
        w = extract_words(sentence)
        words.extend(w)
        
    words = sorted(list(set(words)))
    return words

def extract_words(sentence):
    ignore_words = ['a']
    words = re.sub("[^\w]", " ",  sentence).split() #nltk.word_tokenize(sentence)
    words_cleaned = [w.lower() for w in words if w not in ignore_words]
    return words_cleaned    
    
def bagofwords(sentence, words):
    sentence_words = extract_words(sentence)
    # frequency word count
    bag = np.zeros(len(words))
    for sw in sentence_words:
        for i,word in enumerate(words):
            if word == sw: 
                bag[i] += 1
                
    return np.array(bag)

for company in companies:
	filename = company.replace(" ", "-") + "-data.json"
	#csv_filename = company.replace(" ", "-") + '-data.csv'
	for label in labels:

		# create directory
		# for directory in directories:
		# 	if not os.path.exists(directory):
		# 		os.makedirs(directory)

		#csv = open('data/bag-of-word/' + label + '/' + csv_filename, "w", encoding="utf-8")
		with open('data/labelled/' + label + '/' + filename) as json_file:
			data = json.load(json_file)
			sentence = []
			dataset = []
			for key_json, value_json in data.items():
				sentence.append(value_json['article'])
				vocabulary = tokenize_sentences(sentence)
				dataset.append(vocabulary)
				#print(dataset)	
				
			# header = 'articles,'
			# header = header + ",".join(vocabulary) + "\n"
			# csv.write(header)

			# display true or false in the itemlist
			te = TransactionEncoder()
			te_ary = te.fit(dataset).transform(dataset)
			df = pd.DataFrame(te_ary, columns=te.columns_)
			print(df)

			print(apriori(df, min_support=0.6))

			# for key_json, value_json in data.items():
			# 	result = bagofwords(value_json['article'], vocabulary)
			# 	data = key_json + ","
			# 	data = data + ",".join(map(str, result.tolist())) + "\n"
				#csv.write(data)

		#csv.close()
				

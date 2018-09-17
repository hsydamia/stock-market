import numpy as np
import json
import os

companies = [
    "maybank",
    "axiata",
    "cimb",
    "petronas",
    "sime darby"
]

for company in companies:
	with open('data/cleaned/' + company.replace(" ", "-") + '-data.json') as json_file:
		data = json.load(json_file)

		duplicate_total = 0
		#loop for key and value for json file
		for key_json, value_json in data.items():
			for key_to_compared, value_to_compared in data.items():
				if key_json != key_to_compared:
					if value_json == value_to_compared:
						duplicate_total += 1
						print(value_json['title'] + " ->>>>>> DUPLICATE!!!!!!!")

		print('TOTAL DUPLICATE ' + company.upper() + " : " + str(duplicate_total))
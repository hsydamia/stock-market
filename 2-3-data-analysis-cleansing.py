import numpy as np
import json
import os
import itertools
import threading
import time
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

companies = [
    "maybank",
    "axiata",
    "cimb",
    "petronas",
    "sime darby"
]

directories = [
	'data/cleaned',
	'data/dirty'
]

done = False
def animate():
    for c in itertools.cycle(['.', '..', '...', '....']):
        if done:
            break
        sys.stdout.write('\rAnalysing' + c)
        sys.stdout.flush()
        time.sleep(0.1)

for company in companies:
	print(company.upper() + " : " + bcolors.WARNING + '------- START ANALYSE AND REMOVE DUPLICATE -------' + bcolors.ENDC)
	t = threading.Thread(target=animate)
	t.start()
	with open('raw/' + company.replace(" ", "-") + '-data.json') as json_file:
		data = json.load(json_file)

		# create directory
		for directory in directories:
			if not os.path.exists(directory):
				os.makedirs(directory)
		
		# create file
		filename = company.replace(" ", "-") + "-data.json"
		cleaned_data_file = open("cleaned/" + filename, "w", encoding="utf-8")
		dirty_data_file = open('dirty/' + filename, "w", encoding="utf-8")

		# create clean dict and dirty dict
		clean_dict = {}
		dirty_dict = {}
		clean_index = 0
		dirty_index = 0

		#loop for key and value for json file
		for key_json, value_json in data.items():
			for key_to_compared, value_to_compared in data.items():
				if key_json != key_to_compared:
					if value_json != value_to_compared:
						if value_json not in clean_dict.values():
							clean_dict[clean_index] = value_json
							clean_index += 1
					else:
						if value_json not in dirty_dict.values():
							dirty_dict[dirty_index] = value_json
							dirty_index += 1

		# write to clean file
		data_to_write = json.dumps(clean_dict)
		cleaned_data_file.write(data_to_write)
		cleaned_data_file.close()

		# write to dirty file
		data_to_write = json.dumps(dirty_dict)
		dirty_data_file.write(data_to_write)
		dirty_data_file.close()

		print("")
		print(company.upper() + " : " + bcolors.OKGREEN + 'Total raw article: ' + str(len(data)) + bcolors.ENDC)
		print(company.upper() + " : " + bcolors.OKGREEN + 'Total clean data: ' + str(clean_index) + bcolors.ENDC)
		print(company.upper() + " : " + bcolors.OKGREEN + 'Total removed data: ' + str(dirty_index) + bcolors.ENDC)
		print(company.upper() + " : " + bcolors.WARNING + '------- ANALYSE AND REMOVE DUPLICATE DONE -------' + bcolors.ENDC)
		print("")

done = True
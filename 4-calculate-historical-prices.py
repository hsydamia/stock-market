import csv
import math

companies = [
	"maybank",
	"axiata",
	"cimb",
	"petronas",
	"sime darby"
]

for company in companies:
	filename = company.replace(" ", "-") + '-historical-prices.csv'
	with open('historical-prices/raw/' + filename) as csv_file:
		data = csv.reader(csv_file, delimiter=',')
		next(data, None)

		# create file
		calculated_data_file = open('historical-prices/calculated/' + filename, "w")

		# Index - Data
		# 0 - Date, 1 - Open, 2 - High, 3 - Low, 4- Close, 5- Adj Close, 6 - Volume
		for row in data:
			if (row[0] != 'null' and (row[1] != 'null' and math.ceil(float(row[1])) != 0) and row[4] != 'null'):
				y = (float(row[4]) - float(row[1])) / float(row[1])

				write_to_file = ','.join(map(str, row)) + ',' + str(y) + "\n"
				calculated_data_file.write(write_to_file)
				print(company + ': ' + write_to_file)

	calculated_data_file.close()
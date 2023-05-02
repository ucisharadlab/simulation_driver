import csv
from math import comb
import matplotlib.pyplot as plotlib
import numpy as np

def get_rows(full_path: str) -> list:
    rows = list()
    with open(full_path, 'r') as file:
        reader = csv.reader(file, delimiter="\t", quoting = csv.QUOTE_NONNUMERIC)
        for row in reader:
            rows.append(row)
    return rows

all_data = np.asarray(get_rows('/Users/sriramrao/Downloads/measures/perimeter_res_measures.tsv'))

perimeter_res = [15, 30, 45, 60, 75, 90]
colours = ['red', 'blue', 'cyan', 'orange', 'black', 'pink', 'green']

print(len(all_data[0]))

data = list()
# for i in range(0, len(perimeter_res)):
# 	data = list()
# 	for row in all_data:
# 		if int(row[3]) != perimeter_res[i]:
# 			continue
# 		data.append(row)
# 	data = np.asarray(data)
# 	plotlib.plot(data[:, 2], data[:, 4], color=colours[i], alpha=0.65)

for row in all_data:
	if int(row[2]) != 3:
		continue
	data.append(row)
data = np.asarray(data)
plotlib.plot(data[:, 3], data[:, 4], color='blue', alpha=0.65)
plotlib.xlabel("perimeter resolution")
plotlib.ylabel("latency")
plotlib.show()

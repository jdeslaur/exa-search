import json
import csv
import numpy as np
from tqdm import tqdm
from sklearn.cluster import DBSCAN
from fuzzywuzzy import fuzz


filePath = '/Users/justin/Documents/user_entities_clean'
userStrings = []


with open(filePath, 'r') as file:
    total_lines = sum(1 for line in file)
with open(filePath, 'r') as file:
    for line in tqdm(file, total=total_lines, desc="Processing lines"):
        userStrings.append(line.strip())
    

with tqdm(total=len(userStrings) * len(userStrings), desc="Calculating similarity matrix") as pbar:
    for i in range(len(userStrings)):
        for j in range(len(userStrings)):
            similarity_matrix = np.zeros((len(userStrings), len(userStrings)))
            pbar.update(1)

for i in range(len(userStrings)):
    for j in range(len(userStrings)):
        similarity_matrix[i][j] = fuzz.ratio(userStrings[i],userStrings[j])

distance_matrix = 100 - similarity_matrix
epsValues = [40,50,60]
for epsValue in epsValues:
    clustering = DBSCAN(eps=epsValue, min_samples=2, metric='precomputed').fit(distance_matrix)
    outputFilePath = f'/Users/justin/Downloads/clustered_user_{epsValue}.csv'
    with open(outputFilePath, 'w', newline='') as csvfile:
        fieldNames = ['user','cluster']
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        writer.writeheader()
        for i, label in enumerate(clustering.labels_):
           writer.writerow({'user': userStrings[i], 'cluster':label})

import json
import csv
import numpy as np
from tqdm import tqdm
from sklearn.cluster import DBSCAN
from fuzzywuzzy import fuzz
from multiprocessing import Pool, cpu_count

filePath = '/Users/justin/Documents/user_entities_clean'
outputDir = '/Users/justin/Downloads'

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def calculate_similarity(args):
    i, userStrings = args
    return [fuzz.ratio(userStrings[i], userStrings[j]) for j in range(len(userStrings))]

def main():
    userStrings = read_file(filePath)
    total_strings = len(userStrings)

    # Parallel similarity matrix computation
    with Pool(cpu_count()) as pool:
        similarity_matrix = list(tqdm(pool.imap(calculate_similarity, [(i, userStrings) for i in range(total_strings)]), total=total_strings, desc="Calculating similarity matrix"))

    similarity_matrix = np.array(similarity_matrix)
    distance_matrix = 100 - similarity_matrix

    epsValues = [40, 50, 60]
    for epsValue in epsValues:
        clustering = DBSCAN(eps=epsValue, min_samples=2, metric='precomputed').fit(distance_matrix)
        outputFilePath = f'{outputDir}/clustered_user_{epsValue}.csv'
        with open(outputFilePath, 'w', newline='') as csvfile:
            fieldNames = ['user', 'cluster']
            writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
            writer.writeheader()
            for i, label in enumerate(clustering.labels_):
                writer.writerow({'user': userStrings[i], 'cluster': label})

if __name__ == "__main__":
    main()

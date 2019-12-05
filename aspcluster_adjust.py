import numpy as np
import pandas as pd
import argparse
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn import metrics, preprocessing
import sys

FACTOR = 0

def main():
     # Handling command line arguments
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', nargs='?', type=str, help="Target Classification Field if any")
    parser.add_argument('k', type=int, help="K-Means K")

    args = parser.parse_args()

    data = pd.read_csv(args.file)
    
    X = data
    if args.target:
        X = X.drop(columns=[args.target])

    cl = KMeans(n_clusters = args.k).fit(X)
    labels_pred = cl.predict(X)
    centroids = cl.cluster_centers_
    data = data.assign(predtarget = labels_pred)

    # Data now contains the original data with the predicted cluster
    # Detect Factor prior to transforming data to ASP
    powerfactor = 0
    for index, row in X.iterrows():
        for val in row:
            try:
                if (isinstance(val, float)):
                    sep = str(val).split('.')
                    if (len(sep) == 2):
                        powerfactor = max(powerfactor, len(sep[1]))
            except ValueError:
                pass
    
    global FACTOR
    FACTOR = pow(10, powerfactor)

    dicts = data.to_dict(orient='records')
    asp_facts = ""
    for att in dicts[0].keys():
        asp_facts += "attribute('{0}'). ".format(att)
    asp_facts += "\n"
    if args.target:
        asp_facts += "classtarget('{0}').\n".format(args.target)
    asp_facts += "predtarget('predtarget').\n"
    for i,d in enumerate(dicts):
        for k,v in d.items():
            if k == args.target:
                asp_facts += "class({0}, 'c_{1}'). ".format(i,str(v).replace('-','_').lower())
            elif k == 'predtarget':
                asp_facts += "cluster({0}, 'p_{1}'). ".format(i,str(v).replace('-','_').lower())
            else:
                asp_facts += "value({0},'{1}',{2:d}). ".format(i,k,int(float(v)*FACTOR))
        asp_facts += "\n"
    
    

if __name__ == "__main__":
    main()
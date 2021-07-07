import pandas as pd
from aspbeef import main as beef
import argparse
import time
import tempfile
from itertools import product
import random

def main():
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', type=str, help="Target Feature")
    parser.add_argument('k', type=int, help="K for KMeans")
    parser.add_argument('-i', '--iters', type=int, default=10, help="Number of time to perform each BEEF")
    args = parser.parse_args()

    data = pd.read_csv(args.file)
    data_no_target = data.drop(columns=[args.target])
    dicts = data_no_target.to_dict(orient='records')
    data_features = list(dicts[0].keys())
    
    attr_sizes = list(range(2,5))
    sample_sizes = [60, 90, 150]

    
    cases = product(attr_sizes, sample_sizes)


    with open("beeftimes.csv", "w") as outfile:
        outfile.write("sample_size,\tfeatures,\tfreetime,\tfixedtime\n")
        for attr,samp in cases:
            with tempfile.NamedTemporaryFile() as temp_file:
                sample = data.sample(samp)
                sample.to_csv(temp_file.name, index=False)

                beefargs_free = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr)]

                free_exectime = 0
                fixed_exectime = 0
                for i in range(args.iters):
                    start = time.time()
                    beef(beefargs_free)
                    end = time.time()
                    free_exectime += end-start

                    sel_features = random.sample(data_features, attr)
                    beefargs_sel = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr), "-s"] + sel_features
                    start = time.time()
                    beef(beefargs_sel)
                    end = time.time()
                    fixed_exectime += end-start
                avg_exectime_free = free_exectime/args.iters
                avg_exectime_fixed = fixed_exectime/args.iters
            
            outfile.write(f"{samp},\t{attr},\t{avg_exectime_free:.4f}\t{avg_exectime_fixed:.4f}\n")




if __name__ == "__main__":
    main()
import pandas as pd
from aspbeef import main as beef
import argparse
import time
import tempfile
from itertools import product
import random
import io
from contextlib import redirect_stdout

import contextlib, io

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

    index = data.index
    number_of_rows = len(index)
    
    #attr_sizes = list(range(2,len(data.columns)))
    #sample_sizes = [(number_of_rows//5)*2, (number_of_rows//5)*3, (number_of_rows)]
    

    # NOTA: Llamar a beef() genera un tmp_facts.lp con cada llamada
    # Estuve comentando y descomentando cosas para generar el tmp_facts a mi gusto y ejecutarlo con asprin


    attr_sizes = [3]
    sample_sizes = [number_of_rows]

    cases = product(attr_sizes, sample_sizes)
    with open("beeftimes.csv", "w") as outfile:
        outfile.write("sample_size,\tfeatures,\tfreetime,\tfixedtime\n")
        print("sample_size,\tfeatures,\tfreetime,\tfixedtime\n")
        for attr,samp in cases:
            with tempfile.NamedTemporaryFile() as temp_file:
                sample = data.sample(samp)
                sample.to_csv(temp_file.name, index=False)

                beefargs_free = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr)]

                free_exectime = 0
                fixed_exectime = 0
                #print(f"ATTRS: {attr} // SAMPLES: {samp}")
                for i in range(args.iters):
                    freestart = time.time()
                    f = io.StringIO()
                    #beef(beefargs_free + ["-si", "-np", "-st"])
                    freeend = time.time()
                    free_exectime += freeend-freestart

                    #print(f"#{i} Free Time: {freeend-freestart:.4f}")

                    sel_features = random.sample(data_features, attr)
                    
                    beefargs_sel = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr), "-s"] + sel_features
                    fixedstart = time.time()
                    beef(beefargs_sel   + ["-si", "-np", "-st"])
                    fixedend = time.time()
                    fixed_exectime += fixedend-fixedstart

                    #print(f"#{i} Fixed Time: {fixedend-fixedstart:.4f}")
                avg_exectime_free = free_exectime/args.iters
                avg_exectime_fixed = fixed_exectime/args.iters
            print(f"{samp},\t{attr},\t{avg_exectime_free:.4f}\t{avg_exectime_fixed:.4f}")
            outfile.write(f"{samp},\t{attr},\t{avg_exectime_free:.4f}\t{avg_exectime_fixed:.4f}\n")





if __name__ == "__main__":
    main()
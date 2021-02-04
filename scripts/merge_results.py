#! /usr/bin/python3.6

import sys
import os
import pandas as pd

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Incorrect number of arguments! Argument 1 is the first result file to merge. Argument 2 is the second result file to merge. Argument 3 is the output result file.")
        exit(-1)
    
    input_1 = sys.argv[1]
    input_2 = sys.argv[2]
    output = sys.argv[3]
    
    output_folder = os.path.dirname(output)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    df1 = pd.read_csv(input_1)
    df2 = pd.read_csv(input_2)
    df2["run_nb"] += df1.shape[0]
    df3 = df1.append(df2)
    df3.to_csv(output)


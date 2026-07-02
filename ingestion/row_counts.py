import pandas as pd
import glob

for f in glob.glob("data/raw/*.txt"):
    print(f, len(pd.read_csv(f, low_memory=False)))
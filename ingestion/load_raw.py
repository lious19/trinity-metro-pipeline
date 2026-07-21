import pandas as pd
import glob, os
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:trusts@localhost:5432/trinity_metro")

for f in glob.glob("data/raw/*.txt"):
    table = "raw_" + os.path.basename(f).replace(".txt", "")
    df = pd.read_csv(f, low_memory=False)
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"Loaded {len(df):>7} rows -> {table}")
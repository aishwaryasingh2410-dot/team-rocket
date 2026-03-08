import pandas as pd
import os
from backend.db.connection import options_collection

DATA_FOLDER = "data"

files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

total_records = 0

for file in files:
    path = os.path.join(DATA_FOLDER, file)

    print(f"Loading {file}...")

    df = pd.read_csv(path)

    # convert to dictionary
    records = df.to_dict("records")

    if records:
        options_collection.insert_many(records)
        total_records += len(records)

print(f"\nInserted {total_records} records into MongoDB")
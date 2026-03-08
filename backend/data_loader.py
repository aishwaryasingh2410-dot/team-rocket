import os
import glob
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_all_data():

    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

    if len(files) == 0:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

    df.columns = df.columns.str.strip().str.lower()

    return df


def get_available_expiries():

    df = load_all_data()

    if df.empty:
        return []

    return sorted(df["expiry"].dropna().unique())


def load_expiry_data(expiry):

    df = load_all_data()

    if df.empty:
        return df

    return df[df["expiry"] == expiry]
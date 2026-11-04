import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

df = pd.read_csv(DATA_DIR / "cleaned_tickets.csv")

print("\n=== DATASET OVERVIEW ===")
print(df.info())

print("\n=== TICKETS BY PRODUCT ===")
print(df["product"].value_counts())

print("\n=== TICKETS BY STATUS ===")
print(df["status"].value_counts())

print("\n=== TICKETS BY PRIORITY ===")
print(df["priority"].value_counts())

print("\n=== HIGH PRIORITY OPEN TICKETS ===")

high_priority = df[
    (df["priority"].isin(["High", "Critical"])) &
    (df["status"] == "Open")
]

print(high_priority.head(10))
print(f"\nTotal: {len(high_priority)}")
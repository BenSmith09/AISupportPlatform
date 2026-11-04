
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def clean_tickets():
    # EXTRACT: Load raw CSV into a DataFrame
    df = pd.read_csv(DATA_DIR / "raw_tickets.csv")

    print(f"Original rows: {len(df)}")

    # TRANSFORM: Remove duplicate ticket IDs
    df = df.drop_duplicates(subset=["ticket_id"])
    print(f"After removing duplicates: {len(df)}")

    # Handle missing product values
    missing_products = df["product"].isna().sum()
    print(f"Missing product values: {missing_products}")

    df["product"] = df["product"].fillna("Unknown")

    # Standardise text formatting
    df["customer"] = df["customer"].str.strip()
    df["product"] = df["product"].str.strip()
    df["status"] = df["status"].str.strip()

    # Convert dates into proper datetime values
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    # Remove records with invalid dates
    df = df.dropna(subset=["created_at"])

    # Sort records by creation date
    df = df.sort_values("created_at")

    # LOAD: Save cleaned data to a new CSV
    output_file = DATA_DIR / "cleaned_tickets.csv"

    df.to_csv(output_file, index=False)

    print(f"Final cleaned rows: {len(df)}")
    print(f"Saved to: {output_file}")

    return df


if __name__ == "__main__":
    clean_tickets()

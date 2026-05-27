"""Ingest CSV/Excel input with case numbers and addresses."""
import pandas as pd
from pathlib import Path

REQUIRED_COLS = ["case_number", "address", "appraised_value"]

def load_cases(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Input missing required columns: {missing}. Got: {list(df.columns)}")

    df["appraised_value"] = pd.to_numeric(df["appraised_value"], errors="coerce")
    return df.reset_index(drop=True)

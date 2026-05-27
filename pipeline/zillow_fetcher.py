"""
Zillow property data via RapidAPI (Zillow56 endpoint).
Extracts: year_built, sqft, bathrooms, zestimate, rent_zestimate.
Set RAPIDAPI_KEY in your .env file.
"""
import os, time
from typing import Optional

ZILLOW_HOST = "zillow56.p.rapidapi.com"

def fetch_zillow(df, demo: bool = False):
    import pandas as pd
    cols = ["year_built", "sqft", "bathrooms", "zestimate", "rent_zestimate"]
    for c in cols:
        df[c] = None

    if demo:
        sample = [
            (1987, 1420, 2.0, 142000, 1050),
            (2001, 1850, 3.0, 198000, 1400),
            (1972, 1100, 1.0, 95000, 780),
            (1995, 2200, 3.5, 265000, 1750),
            (2008, 1650, 2.0, 175000, 1200),
        ]
        for i, vals in enumerate(sample[:len(df)]):
            df.at[i, "year_built"] = vals[0]
            df.at[i, "sqft"] = vals[1]
            df.at[i, "bathrooms"] = vals[2]
            df.at[i, "zestimate"] = vals[3]
            df.at[i, "rent_zestimate"] = vals[4]
        return df

    import requests
    api_key = os.getenv("RAPIDAPI_KEY", "")
    if not api_key:
        print("  [Zillow] RAPIDAPI_KEY not set — skipping Zillow fetch")
        return df

    for idx, row in df.iterrows():
        data = _query_zillow(str(row["address"]), api_key)
        if data:
            for k, v in data.items():
                df.at[idx, k] = v
        time.sleep(1.0)
    return df


def _query_zillow(address: str, api_key: str) -> Optional[dict]:
    import requests
    try:
        r = requests.get(
            f"https://{ZILLOW_HOST}/search",
            params={"location": address},
            headers={"x-rapidapi-key": api_key, "x-rapidapi-host": ZILLOW_HOST},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        props = data.get("props", [])
        if not props:
            return None
        p = props[0]
        return {
            "year_built": p.get("yearBuilt"),
            "sqft": p.get("livingArea"),
            "bathrooms": p.get("bathrooms"),
            "zestimate": p.get("zestimate"),
            "rent_zestimate": p.get("rentZestimate"),
        }
    except Exception:
        return None

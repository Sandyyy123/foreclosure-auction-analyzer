"""
Logic filter engine: flags high HOA, single-bath, over-appraised assets.
Computes Price-to-Rent Ratio for ranking.
"""
import pandas as pd

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    df["warnings"] = ""
    df["price_to_rent_ratio"] = None
    df["recommendation"] = "Review"

    for idx, row in df.iterrows():
        warnings = []

        # Flag: single bathroom
        if pd.notna(row.get("bathrooms")) and row["bathrooms"] <= 1.0:
            warnings.append("Single bath - low rental demand")

        # Flag: over-appraised (Zestimate < 90% of appraised value)
        appraised = row.get("appraised_value")
        zestimate = row.get("zestimate")
        if pd.notna(appraised) and pd.notna(zestimate) and appraised > 0:
            if zestimate < appraised * 0.90:
                pct = round((1 - zestimate / appraised) * 100, 1)
                warnings.append(f"Over-appraised by {pct}% vs Zestimate")

        # Flag: lien warnings from OSCN
        if row.get("oscn_warning"):
            warnings.append("Junior lienholder detected - title risk")

        # Price-to-Rent Ratio
        rent = row.get("rent_zestimate")
        if pd.notna(appraised) and pd.notna(rent) and rent > 0:
            annual_rent = rent * 12
            ptr = round(appraised / annual_rent, 2)
            df.at[idx, "price_to_rent_ratio"] = ptr
            if ptr <= 15:
                df.at[idx, "recommendation"] = "BUY"
            elif ptr <= 20:
                df.at[idx, "recommendation"] = "HOLD"
            else:
                df.at[idx, "recommendation"] = "SKIP"
                warnings.append(f"High P/R ratio: {ptr}")

        df.at[idx, "warnings"] = " | ".join(warnings)

    return df

# Foreclosure Auction Analyzer

Automated pipeline for Oklahoma foreclosure auction analysis. Pulls OSCN court dockets, Zillow property metrics, applies lien/risk filters, and outputs a ranked Excel spreadsheet sorted by Price-to-Rent Ratio.

## Architecture

```
Input CSV/Excel
     |
     v
[Ingestor] --> parse case_number / address / appraised_value
     |
     v
[OSCN Scraper] --> Playwright stealth scrape --> lien_flags, oscn_warning
     |
     v
[Zillow Fetcher] --> RapidAPI (Zillow56) --> zestimate, rent_zestimate, sqft, baths
     |
     v
[Filter Engine] --> HOA flag / single-bath / over-appraised / P/R ratio
     |
     v
[Exporter] --> color-coded Excel sorted by Price-to-Rent Ratio
```

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env    # add your RAPIDAPI_KEY
```

## Usage

```bash
# Demo mode (no network calls, uses sample data)
python main.py --demo

# Live run
python main.py --input data/my_cases.csv --output results/output.xlsx
```

## Input Format

| column | type | example |
|--------|------|---------|
| case_number | string | CJ-2024-1234 |
| address | string | 1420 NW 32nd St, Oklahoma City, OK |
| appraised_value | number | 142000 |

## Output Columns

| column | description |
|--------|-------------|
| price_to_rent_ratio | appraised_value / (rent_zestimate * 12) |
| recommendation | BUY (<= 15), HOLD (<= 20), SKIP (> 20) |
| lien_flags | Junior lienholders found in OSCN docket |
| warnings | Filter alerts: over-appraised, single-bath, etc. |

## Pricing logic
- P/R <= 15: **BUY** (strong rental yield)
- P/R 15-20: **HOLD** (acceptable)
- P/R > 20: **SKIP** (over-priced for rental)

## Author
Dr. Sandeep Grover | Python Automation & Data Engineering

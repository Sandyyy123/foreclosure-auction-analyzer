#!/usr/bin/env python3
"""
Foreclosure Auction Analyzer
Run: python main.py --input data/sample_cases.csv --output results/output.xlsx
"""
import argparse
from pathlib import Path
from pipeline.ingestor import load_cases
from pipeline.oscn_scraper import scrape_oscn
from pipeline.zillow_fetcher import fetch_zillow
from pipeline.filter_engine import apply_filters
from pipeline.exporter import export_ranked

def main():
    parser = argparse.ArgumentParser(description="Foreclosure Auction Analyzer")
    parser.add_argument("--input", default="data/sample_cases.csv", help="Input CSV/Excel path")
    parser.add_argument("--output", default="results/output.xlsx", help="Output Excel path")
    parser.add_argument("--demo", action="store_true", help="Run with sample data (no network calls)")
    args = parser.parse_args()

    print("\n=== Foreclosure Auction Analyzer ===")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}\n")

    # Step 1: Load input
    cases = load_cases(args.input)
    print(f"[1/4] Loaded {len(cases)} cases")

    # Step 2: OSCN court docket scraping
    cases = scrape_oscn(cases, demo=args.demo)
    print(f"[2/4] OSCN dockets scraped")

    # Step 3: Zillow property data
    cases = fetch_zillow(cases, demo=args.demo)
    print(f"[3/4] Zillow data fetched")

    # Step 4: Filter + rank + export
    cases = apply_filters(cases)
    output_path = export_ranked(cases, args.output)
    print(f"[4/4] Output saved: {output_path}")
    print("\n=== Complete ===")

if __name__ == "__main__":
    main()

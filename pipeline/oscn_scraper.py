"""
OSCN.net court docket scraper with stealth Playwright.
Detects junior lienholders: HOA, second mortgages, judgment creditors.
"""
import time, random
from typing import Optional

LIEN_KEYWORDS = [
    "gitsit", "hoa", "homeowners association", "second mortgage",
    "judgment lien", "mechanic lien", "irs", "tax lien", "municipal lien"
]

def scrape_oscn(df, demo: bool = False):
    """Scrape OSCN docket for each case. Returns df with lien_flags and raw_docket columns."""
    import pandas as pd

    df["lien_flags"] = ""
    df["docket_text"] = ""
    df["oscn_warning"] = False

    if demo:
        # Inject sample flags for demonstration
        sample_flags = ["HOA judgment ($8,200)", "Gitsit Solutions lien", "", "Second mortgage (Chase)", ""]
        for i, flags in enumerate(sample_flags[:len(df)]):
            df.at[i, "lien_flags"] = flags
            df.at[i, "oscn_warning"] = bool(flags)
        return df

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [OSCN] Playwright not installed. Run: pip install playwright && playwright install chromium")
        return df

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage"
            ]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        page = ctx.new_page()

        for idx, row in df.iterrows():
            case_num = str(row["case_number"]).strip()
            flags = _fetch_docket(page, case_num)
            df.at[idx, "lien_flags"] = "; ".join(flags)
            df.at[idx, "oscn_warning"] = len(flags) > 0
            time.sleep(random.uniform(1.5, 3.5))  # polite crawl delay

        browser.close()
    return df


def _fetch_docket(page, case_number: str) -> list:
    """Fetch OSCN docket page and extract lien-related plaintiff names."""
    flags = []
    try:
        url = f"https://www.oscn.net/dockets/GetCaseInformation.aspx?db=oklahoma&number={case_number}"
        page.goto(url, timeout=20000, wait_until="domcontentloaded")
        text = page.inner_text("body").lower()

        for kw in LIEN_KEYWORDS:
            if kw in text:
                flags.append(kw.title())
    except Exception as e:
        flags.append(f"ERROR: {str(e)[:60]}")
    return flags

"""
S&P 500 List Utility
Maintains list of S&P 500 tickers with update functionality
"""

from typing import List, Set
import httpx

# Optional import for Wikipedia scraping (only needed for updates)
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Hardcoded S&P 500 list (updated as of 2024)
# This list includes the major components - can be expanded
SP500_TICKERS = {
    # Technology
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "CSCO", "ACN", "AMD",
    "IBM", "INTU", "TXN", "QCOM", "NOW", "PANW", "AMAT", "ADI", "MU", "LRCX",
    "KLAC", "SNPS", "CDNS", "MCHP", "FTNT", "ANSS", "TRMB", "EPAM", "GEN",
    
    # Healthcare
    "UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO", "ABT", "AMGN", "DHR", "PFE",
    "BMY", "ISRG", "VRTX", "GILD", "CVS", "CI", "ELV", "HUM", "REGN", "MCK",
    "COR", "ZTS", "IDXX", "BDX", "SYK", "BSX", "EW", "MTD", "A", "IQV",
    
    # Financials
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "SPGI", "BLK",
    "C", "AXP", "CB", "PGR", "MMC", "SCHW", "USB", "PNC", "TFC", "COF",
    "CME", "ICE", "AON", "BK", "AJG", "AFL", "MET", "ALL", "PRU", "TRV",
    
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG",
    "MAR", "ABNB", "GM", "F", "ORLY", "AZO", "DHI", "LEN", "YUM", "RCL",
    "CCL", "NCLH", "HLT", "MGM", "LVS", "WYNN", "GRMN", "POOL", "TPR",
    
    # Consumer Staples
    "WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ", "CL", "GIS",
    "KHC", "HSY", "K", "STZ", "ADM", "SYY", "KMB", "CHD", "CLX", "CPB",
    
    # Communication Services
    "META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR",
    "EA", "TTWO", "MTCH", "FOXA", "FOX", "OMC", "IPG", "NWSA", "NWS",
    
    # Industrials
    "UNP", "CAT", "RTX", "HON", "UPS", "BA", "GE", "LMT", "DE", "ADP",
    "NOC", "MMM", "GD", "ETN", "ITW", "CSX", "EMR", "NSC", "WM", "FDX",
    "PCAR", "JCI", "TT", "CMI", "PH", "RSG", "FAST", "VRSK", "ODFL", "PWR",
    
    # Materials
    "LIN", "APD", "SHW", "ECL", "FCX", "NEM", "CTVA", "DD", "NUE", "DOW",
    "PPG", "IFF", "CE", "VMC", "MLM", "ALB", "BALL", "AVY", "PKG", "IP",
    
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HES",
    "WMB", "KMI", "OKE", "HAL", "BKR", "FANG", "DVN", "MRO", "APA",
    
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "ED", "WEC",
    "PEG", "ES", "AWK", "DTE", "EIX", "PPL", "FE", "AEE", "CMS", "CNP",
    
    # Real Estate
    "PLD", "AMT", "EQIX", "CCI", "PSA", "SPG", "WELL", "DLR", "O", "VICI",
    "AVB", "EQR", "SBAC", "VTR", "ARE", "INVH", "MAA", "ESS", "UDR", "CPT",
    
    # ETFs (commonly held)
    "URA", "IAU", "SLV", "IBIT", "MAGS",
    
    # Other major holdings
    "PLTR", "CSV"
}

def is_sp500(ticker: str) -> bool:
    """Check if a ticker is in the S&P 500"""
    return ticker.upper() in SP500_TICKERS

def filter_sp500(tickers: List[str]) -> List[str]:
    """Filter a list of tickers to only include S&P 500 stocks"""
    return [t for t in tickers if is_sp500(t)]

def get_sp500_list() -> List[str]:
    """Get the full S&P 500 list"""
    return sorted(list(SP500_TICKERS))

def get_sp500_by_sector(sector: str) -> List[str]:
    """Get S&P 500 stocks filtered by sector (simplified)"""
    # This is a simplified mapping - in production would use sector_classifier
    sector_mapping = {
        "Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "CSCO", "ACN", "AMD"],
        "Healthcare": ["UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO", "ABT", "AMGN", "DHR", "PFE"],
        "Financials": ["BRK.B", "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "SPGI", "BLK"],
        "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX"],
        "Consumer Staples": ["WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ"],
        "Communication Services": ["META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "T", "VZ"],
        "Industrials": ["UNP", "CAT", "RTX", "HON", "UPS", "BA", "GE", "LMT", "DE"],
        "Materials": ["LIN", "APD", "SHW", "ECL", "FCX", "NEM", "CTVA", "DD"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO"],
        "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL"],
        "Real Estate": ["PLD", "AMT", "EQIX", "CCI", "PSA", "SPG", "WELL", "DLR"]
    }
    
    return sector_mapping.get(sector, [])

async def update_sp500_list_from_wikipedia() -> List[str]:
    """
    Update S&P 500 list by fetching from Wikipedia
    This is a manual/scheduled operation, not called frequently
    Requires BeautifulSoup4: pip install beautifulsoup4
    """
    if not BS4_AVAILABLE:
        print("⚠️ BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
        return get_sp500_list()
    
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch S&P 500 list: {response.status_code}")
                return get_sp500_list()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})
            
            if not table:
                print("⚠️ Could not find S&P 500 table on Wikipedia")
                return get_sp500_list()
            
            tickers = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    ticker = cells[0].text.strip()
                    # Clean up ticker (remove any trailing characters)
                    ticker = ticker.replace('\n', '').strip()
                    tickers.append(ticker)
            
            print(f"✅ Fetched {len(tickers)} S&P 500 tickers from Wikipedia")
            return sorted(tickers)
    
    except Exception as e:
        print(f"❌ Error fetching S&P 500 list: {e}")
        return get_sp500_list()

# Utility to manually update the hardcoded list
async def print_updated_sp500_list():
    """Helper function to print updated list for manual code update"""
    tickers = await update_sp500_list_from_wikipedia()
    print("\nUpdated SP500_TICKERS = {")
    for ticker in tickers:
        print(f'    "{ticker}",')
    print("}")


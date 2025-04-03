import yfinance as yf
import random

def fetch_stock_data(tickers):
    """
    Fetch current stock data for the given tickers.
    
    Args:
        tickers (list): List of stock ticker symbols
        
    Returns:
        dict: Dictionary of ticker data
    """
    result = {}
    
    try:
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                # Get the latest price
                latest_price = hist['Close'].iloc[-1]
                
                # Get price change percentage (if available)
                try:
                    price_change = stock.info.get('regularMarketChangePercent', 0)
                except:
                    # Calculate from history if not available in info
                    if len(hist) > 1:
                        prev_price = hist['Close'].iloc[-2]
                        price_change = ((latest_price - prev_price) / prev_price) * 100
                    else:
                        price_change = 0
                
                result[ticker] = {
                    'current_price': latest_price,
                    'price_change_percent': price_change
                }
    except Exception as e:
        print(f"Error fetching stock data: {e}")
    
    return result

def get_stock_suggestions(category):
    """
    Get stock suggestions for a given category.
    
    Args:
        category (str): Investment category
        
    Returns:
        list: List of suggested stocks
    """
    suggestions = {
        "Large Cap": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "description": "Technology company that designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
                "risk_rating": "Low"
            },
            {
                "ticker": "MSFT",
                "name": "Microsoft Corporation",
                "description": "Technology company that develops, licenses, and supports software, services, devices, and solutions.",
                "risk_rating": "Low"
            },
            {
                "ticker": "AMZN",
                "name": "Amazon.com, Inc.",
                "description": "E-commerce, cloud computing, digital streaming, and artificial intelligence company.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "description": "Medical devices, pharmaceutical, and consumer packaged goods manufacturer.",
                "risk_rating": "Low"
            },
            {
                "ticker": "PG",
                "name": "Procter & Gamble",
                "description": "Consumer goods corporation that specializes in a wide range of personal health, consumer health, and personal care products.",
                "risk_rating": "Low"
            }
        ],
        "Mid Cap": [
            {
                "ticker": "ETSY",
                "name": "Etsy, Inc.",
                "description": "E-commerce website focused on handmade or vintage items and craft supplies.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "ROKU",
                "name": "Roku, Inc.",
                "description": "Manufacturer of digital media players for streaming entertainment content.",
                "risk_rating": "Medium-High"
            },
            {
                "ticker": "SNAP",
                "name": "Snap Inc.",
                "description": "Camera and social media company that develops Snapchat and Spectacles.",
                "risk_rating": "High"
            },
            {
                "ticker": "DKNG",
                "name": "DraftKings Inc.",
                "description": "Digital sports entertainment and gaming company.",
                "risk_rating": "High"
            },
            {
                "ticker": "ZEN",
                "name": "Zendesk, Inc.",
                "description": "Customer service software company that builds software to improve customer relationships.",
                "risk_rating": "Medium"
            }
        ],
        "Small Cap": [
            {
                "ticker": "SFIX",
                "name": "Stitch Fix, Inc.",
                "description": "Online personal styling service in the United States and United Kingdom.",
                "risk_rating": "High"
            },
            {
                "ticker": "MGNI",
                "name": "Magnite, Inc.",
                "description": "Independent sell-side advertising platform that combines Rubicon Project and Telaria.",
                "risk_rating": "High"
            },
            {
                "ticker": "VUZI",
                "name": "Vuzix Corporation",
                "description": "Supplier of Smart-Glasses and Augmented Reality (AR) technologies and products.",
                "risk_rating": "Very High"
            },
            {
                "ticker": "PUBM",
                "name": "PubMatic, Inc.",
                "description": "Provides a cloud infrastructure platform that enables real-time programmatic advertising transactions.",
                "risk_rating": "High"
            },
            {
                "ticker": "HEAR",
                "name": "Turtle Beach Corporation",
                "description": "Audio technology company that designs and markets audio peripherals for video game consoles, personal computers, and mobile devices.",
                "risk_rating": "High"
            }
        ],
        "Gold": [
            {
                "ticker": "GLD",
                "name": "SPDR Gold Shares",
                "description": "Exchange-traded fund that tracks the price of gold.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "IAU",
                "name": "iShares Gold Trust",
                "description": "Exchange-traded fund designed to reflect the price of gold bullion.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "NEM",
                "name": "Newmont Corporation",
                "description": "World's largest gold mining corporation.",
                "risk_rating": "Medium-High"
            },
            {
                "ticker": "GOLD",
                "name": "Barrick Gold Corporation",
                "description": "Mining company that produces gold and copper.",
                "risk_rating": "Medium-High"
            },
            {
                "ticker": "FNV",
                "name": "Franco-Nevada Corporation",
                "description": "Gold-focused royalty and streaming company with a diversified portfolio of cash-flow producing assets.",
                "risk_rating": "Medium"
            }
        ],
        "ETFs/Crypto": [
            {
                "ticker": "VOO",
                "name": "Vanguard S&P 500 ETF",
                "description": "Exchange-traded fund that tracks the S&P 500 index.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "description": "Exchange-traded fund that tracks the performance of the CRSP US Total Market Index.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "description": "Exchange-traded fund tracking the Nasdaq-100 Index, which includes 100 of the largest non-financial companies listed on the Nasdaq.",
                "risk_rating": "Medium-High"
            },
            {
                "ticker": "GBTC",
                "name": "Grayscale Bitcoin Trust",
                "description": "Investment vehicle that enables investors to gain exposure to Bitcoin in the form of a security.",
                "risk_rating": "Very High"
            },
            {
                "ticker": "ETHE",
                "name": "Grayscale Ethereum Trust",
                "description": "Investment vehicle that enables investors to gain exposure to Ethereum in the form of a security.",
                "risk_rating": "Very High"
            }
        ],
        "Other": [
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "description": "Exchange-traded fund tracking the S&P 500 stock market index.",
                "risk_rating": "Medium"
            },
            {
                "ticker": "ARKK",
                "name": "ARK Innovation ETF",
                "description": "Actively-managed exchange-traded fund that seeks long-term growth of capital.",
                "risk_rating": "High"
            },
            {
                "ticker": "VNQ",
                "name": "Vanguard Real Estate Index Fund",
                "description": "Exchange-traded fund that measures the performance of public traded REITs and other real estate related investments.",
                "risk_rating": "Medium-High"
            },
            {
                "ticker": "BND",
                "name": "Vanguard Total Bond Market ETF",
                "description": "Exchange-traded fund that provides broad exposure to U.S. investment grade bonds.",
                "risk_rating": "Low"
            },
            {
                "ticker": "VXUS",
                "name": "Vanguard Total International Stock ETF",
                "description": "Exchange-traded fund that tracks the performance of stocks issued by companies located in developed and emerging markets, excluding the United States.",
                "risk_rating": "Medium-High"
            }
        ]
    }
    
    return suggestions.get(category, [])

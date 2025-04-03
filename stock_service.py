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

def get_stock_suggestions(category, market="US"):
    """
    Get stock suggestions for a given category.
    
    Args:
        category (str): Investment category
        market (str): Market region (US or India)
        
    Returns:
        list: List of suggested stocks
    """
    us_suggestions = {
        "Large Cap": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "description": "Technology company that designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
                "risk_rating": "Low",
                "sip_available": False
            },
            {
                "ticker": "MSFT",
                "name": "Microsoft Corporation",
                "description": "Technology company that develops, licenses, and supports software, services, devices, and solutions.",
                "risk_rating": "Low",
                "sip_available": False
            },
            {
                "ticker": "AMZN",
                "name": "Amazon.com, Inc.",
                "description": "E-commerce, cloud computing, digital streaming, and artificial intelligence company.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "description": "Medical devices, pharmaceutical, and consumer packaged goods manufacturer.",
                "risk_rating": "Low",
                "sip_available": False
            },
            {
                "ticker": "PG",
                "name": "Procter & Gamble",
                "description": "Consumer goods corporation that specializes in a wide range of personal health, consumer health, and personal care products.",
                "risk_rating": "Low",
                "sip_available": False
            }
        ],
        "Mid Cap": [
            {
                "ticker": "ETSY",
                "name": "Etsy, Inc.",
                "description": "E-commerce website focused on handmade or vintage items and craft supplies.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "ROKU",
                "name": "Roku, Inc.",
                "description": "Manufacturer of digital media players for streaming entertainment content.",
                "risk_rating": "Medium-High",
                "sip_available": False
            },
            {
                "ticker": "SNAP",
                "name": "Snap Inc.",
                "description": "Camera and social media company that develops Snapchat and Spectacles.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "DKNG",
                "name": "DraftKings Inc.",
                "description": "Digital sports entertainment and gaming company.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "ZEN",
                "name": "Zendesk, Inc.",
                "description": "Customer service software company that builds software to improve customer relationships.",
                "risk_rating": "Medium",
                "sip_available": False
            }
        ],
        "Small Cap": [
            {
                "ticker": "SFIX",
                "name": "Stitch Fix, Inc.",
                "description": "Online personal styling service in the United States and United Kingdom.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "MGNI",
                "name": "Magnite, Inc.",
                "description": "Independent sell-side advertising platform that combines Rubicon Project and Telaria.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "VUZI",
                "name": "Vuzix Corporation",
                "description": "Supplier of Smart-Glasses and Augmented Reality (AR) technologies and products.",
                "risk_rating": "Very High",
                "sip_available": False
            },
            {
                "ticker": "PUBM",
                "name": "PubMatic, Inc.",
                "description": "Provides a cloud infrastructure platform that enables real-time programmatic advertising transactions.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "HEAR",
                "name": "Turtle Beach Corporation",
                "description": "Audio technology company that designs and markets audio peripherals for video game consoles, personal computers, and mobile devices.",
                "risk_rating": "High",
                "sip_available": False
            }
        ],
        "Gold": [
            {
                "ticker": "GLD",
                "name": "SPDR Gold Shares",
                "description": "Exchange-traded fund that tracks the price of gold.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "IAU",
                "name": "iShares Gold Trust",
                "description": "Exchange-traded fund designed to reflect the price of gold bullion.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "NEM",
                "name": "Newmont Corporation",
                "description": "World's largest gold mining corporation.",
                "risk_rating": "Medium-High",
                "sip_available": False
            },
            {
                "ticker": "GOLD",
                "name": "Barrick Gold Corporation",
                "description": "Mining company that produces gold and copper.",
                "risk_rating": "Medium-High",
                "sip_available": False
            },
            {
                "ticker": "FNV",
                "name": "Franco-Nevada Corporation",
                "description": "Gold-focused royalty and streaming company with a diversified portfolio of cash-flow producing assets.",
                "risk_rating": "Medium",
                "sip_available": False
            }
        ],
        "ETFs/Crypto": [
            {
                "ticker": "VOO",
                "name": "Vanguard S&P 500 ETF",
                "description": "Exchange-traded fund that tracks the S&P 500 index.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "description": "Exchange-traded fund that tracks the performance of the CRSP US Total Market Index.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "description": "Exchange-traded fund tracking the Nasdaq-100 Index, which includes 100 of the largest non-financial companies listed on the Nasdaq.",
                "risk_rating": "Medium-High",
                "sip_available": False
            },
            {
                "ticker": "GBTC",
                "name": "Grayscale Bitcoin Trust",
                "description": "Investment vehicle that enables investors to gain exposure to Bitcoin in the form of a security.",
                "risk_rating": "Very High",
                "sip_available": False
            },
            {
                "ticker": "ETHE",
                "name": "Grayscale Ethereum Trust",
                "description": "Investment vehicle that enables investors to gain exposure to Ethereum in the form of a security.",
                "risk_rating": "Very High",
                "sip_available": False
            }
        ],
        "Other": [
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "description": "Exchange-traded fund tracking the S&P 500 stock market index.",
                "risk_rating": "Medium",
                "sip_available": False
            },
            {
                "ticker": "ARKK",
                "name": "ARK Innovation ETF",
                "description": "Actively-managed exchange-traded fund that seeks long-term growth of capital.",
                "risk_rating": "High",
                "sip_available": False
            },
            {
                "ticker": "VNQ",
                "name": "Vanguard Real Estate Index Fund",
                "description": "Exchange-traded fund that measures the performance of public traded REITs and other real estate related investments.",
                "risk_rating": "Medium-High",
                "sip_available": False
            },
            {
                "ticker": "BND",
                "name": "Vanguard Total Bond Market ETF",
                "description": "Exchange-traded fund that provides broad exposure to U.S. investment grade bonds.",
                "risk_rating": "Low",
                "sip_available": False
            },
            {
                "ticker": "VXUS",
                "name": "Vanguard Total International Stock ETF",
                "description": "Exchange-traded fund that tracks the performance of stocks issued by companies located in developed and emerging markets, excluding the United States.",
                "risk_rating": "Medium-High",
                "sip_available": False
            }
        ]
    }
    
    india_suggestions = {
        "Large Cap": [
            {
                "ticker": "RELIANCE.NS",
                "name": "Reliance Industries Ltd.",
                "description": "India's largest conglomerate with businesses in energy, petrochemicals, retail, telecommunications, and digital services.",
                "risk_rating": "Low",
                "sip_available": True
            },
            {
                "ticker": "TCS.NS",
                "name": "Tata Consultancy Services Ltd.",
                "description": "India's largest IT services company providing consulting, technology, and digital solutions.",
                "risk_rating": "Low",
                "sip_available": True
            },
            {
                "ticker": "HDFCBANK.NS",
                "name": "HDFC Bank Ltd.",
                "description": "One of India's leading private sector banks with a strong retail banking presence.",
                "risk_rating": "Low",
                "sip_available": True
            },
            {
                "ticker": "INFY.NS",
                "name": "Infosys Ltd.",
                "description": "Global leader in next-generation digital services and consulting.",
                "risk_rating": "Low",
                "sip_available": True
            },
            {
                "ticker": "HINDUNILVR.NS",
                "name": "Hindustan Unilever Ltd.",
                "description": "India's largest fast-moving consumer goods company with products across home care, beauty, personal care, and foods.",
                "risk_rating": "Low",
                "sip_available": True
            }
        ],
        "Mid Cap": [
            {
                "ticker": "JUBLFOOD.NS",
                "name": "Jubilant FoodWorks Ltd.",
                "description": "Operates Domino's Pizza and Dunkin' Donuts chains in India with exclusive rights.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "MPHASIS.NS",
                "name": "Mphasis Ltd.",
                "description": "IT services company specializing in cloud and cognitive services.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "TRENT.NS",
                "name": "Trent Ltd.",
                "description": "Retail chain operator of Westside, Zudio, and Star Bazaar stores.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "COFORGE.NS",
                "name": "Coforge Ltd.",
                "description": "Global digital services and solutions provider specializing in AI, cloud, and data technologies.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "PERSISTENT.NS",
                "name": "Persistent Systems Ltd.",
                "description": "Technology services company specializing in software product development and digital transformation.",
                "risk_rating": "Medium",
                "sip_available": True
            }
        ],
        "Small Cap": [
            {
                "ticker": "KPRMILL.NS",
                "name": "KPR Mill Ltd.",
                "description": "One of the largest vertically integrated textile companies in India, producing yarn, fabrics, and garments.",
                "risk_rating": "High",
                "sip_available": True
            },
            {
                "ticker": "POLYCAB.NS",
                "name": "Polycab India Ltd.",
                "description": "Manufacturer of electrical wires, cables, and fast-moving electrical goods.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "METROPOLIS.NS",
                "name": "Metropolis Healthcare Ltd.",
                "description": "Leading diagnostic and healthcare testing company with a wide network of labs.",
                "risk_rating": "High",
                "sip_available": True
            },
            {
                "ticker": "CDSL.NS",
                "name": "Central Depository Services Ltd.",
                "description": "Depository that holds securities in electronic form and facilitates trading in the stock market.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "INDIAMART.NS",
                "name": "IndiaMART InterMESH Ltd.",
                "description": "B2B marketplace connecting buyers with suppliers across various product categories.",
                "risk_rating": "High",
                "sip_available": True
            }
        ],
        "Gold": [
            {
                "ticker": "GOLDBEES.NS",
                "name": "Nippon India ETF Gold BeES",
                "description": "Exchange-traded fund investing in physical gold, tracking gold prices in India.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "KOTAKGOLD.NS",
                "name": "Kotak Gold ETF",
                "description": "Exchange-traded fund that seeks to provide returns that closely correspond to domestic gold prices.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "HNGSNGBEES.NS",
                "name": "Nippon India ETF Hang Seng BeES",
                "description": "ETF tracking the Hang Seng Index, offering exposure to Hong Kong market including gold companies.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "AXISGOLD.NS",
                "name": "Axis Gold ETF",
                "description": "Exchange-traded fund investing in gold, aimed at providing returns closely corresponding to domestic gold prices.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "HDFCMFGETF.NS",
                "name": "HDFC Gold Exchange Traded Fund",
                "description": "ETF that aims to provide returns that closely track the performance of domestic physical gold prices.",
                "risk_rating": "Medium",
                "sip_available": True
            }
        ],
        "ETFs/Crypto": [
            {
                "ticker": "NIFTYBEES.NS",
                "name": "Nippon India ETF Nifty BeES",
                "description": "ETF tracking the Nifty 50 index, India's benchmark stock market index.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "BANKBEES.NS",
                "name": "Nippon India ETF Bank BeES",
                "description": "ETF tracking the Nifty Bank Index, representing major banks in India.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "KOTAKNIFTY.NS",
                "name": "Kotak Nifty ETF",
                "description": "ETF tracking the Nifty 50 index for diversified exposure to Indian equities.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "SETFNIF50.NS",
                "name": "SBI Nifty 50 ETF",
                "description": "ETF that aims to provide returns closely corresponding to the Nifty 50 index.",
                "risk_rating": "Medium",
                "sip_available": True
            },
            {
                "ticker": "ICICIB22.NS",
                "name": "ICICI Prudential Nifty IT ETF",
                "description": "ETF tracking the Nifty IT index, representing major IT companies in India.",
                "risk_rating": "Medium-High",
                "sip_available": True
            }
        ],
        "Other": [
            {
                "ticker": "LICGFNUT.NS",
                "name": "LIC MF G-Sec Long Term ETF",
                "description": "ETF investing in long-term government securities, aimed at providing safe, fixed income returns.",
                "risk_rating": "Low",
                "sip_available": True
            },
            {
                "ticker": "LIQUIDBEES.NS",
                "name": "Nippon India ETF Liquid BeES",
                "description": "Liquid exchange-traded fund investing in money market instruments.",
                "risk_rating": "Very Low",
                "sip_available": True
            },
            {
                "ticker": "ICICINXT50.NS",
                "name": "ICICI Prudential NIfty Next 50 ETF",
                "description": "ETF tracking the Nifty Next 50 index, representing the next 50 companies after the Nifty 50.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "NETFIT.NS",
                "name": "NIPPON INDIA ETF NIFTY IT",
                "description": "ETF tracking the Nifty IT index, focusing on top IT companies in India.",
                "risk_rating": "Medium-High",
                "sip_available": True
            },
            {
                "ticker": "SBIETFQLTY.NS",
                "name": "SBI Nifty 200 Quality 30 ETF",
                "description": "ETF that tracks the Nifty 200 Quality 30 index, focusing on high-quality stocks based on return on equity, financial leverage, and earnings growth variability.",
                "risk_rating": "Medium",
                "sip_available": True
            }
        ]
    }
    
    if market.upper() == "INDIA":
        return india_suggestions.get(category, [])
    else:
        return us_suggestions.get(category, [])

def get_sip_suggestions(category, market="INDIA"):
    """
    Get SIP suggestions for a given category.
    
    Args:
        category (str): Investment category
        market (str): Market region (primarily India for SIPs)
        
    Returns:
        list: List of suggested SIP mutual funds
    """
    india_sip_suggestions = {
        "Large Cap": [
            {
                "code": "HDFC_TOP_100",
                "name": "HDFC Top 100 Fund",
                "description": "Fund that invests in top 100 companies by market capitalization.",
                "risk_rating": "Low",
                "min_investment": 1000,
                "expense_ratio": 1.75
            },
            {
                "code": "AXIS_BLUECHIP",
                "name": "Axis Bluechip Fund",
                "description": "Invests in bluechip companies with stable growth and high dividend potential.",
                "risk_rating": "Low",
                "min_investment": 500,
                "expense_ratio": 1.56
            },
            {
                "code": "MIRAE_LARGE_CAP",
                "name": "Mirae Asset Large Cap Fund",
                "description": "Invests in large-cap companies with a focus on sustainable growth.",
                "risk_rating": "Low",
                "min_investment": 1000,
                "expense_ratio": 1.58
            },
            {
                "code": "SBI_BLUECHIP",
                "name": "SBI Blue Chip Fund",
                "description": "Focuses on large-cap companies with established business models.",
                "risk_rating": "Low",
                "min_investment": 500,
                "expense_ratio": 1.78
            },
            {
                "code": "ICICI_BLUECHIP",
                "name": "ICICI Prudential Bluechip Fund",
                "description": "Invests in blue-chip companies with a history of stable performance.",
                "risk_rating": "Low",
                "min_investment": 100,
                "expense_ratio": 1.68
            }
        ],
        "Mid Cap": [
            {
                "code": "KOTAK_MIDCAP",
                "name": "Kotak Midcap Fund",
                "description": "Focuses on mid-sized companies with growth potential.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 1.83
            },
            {
                "code": "HDFC_MIDCAP",
                "name": "HDFC Mid-Cap Opportunities Fund",
                "description": "Invests in promising mid-cap companies across sectors.",
                "risk_rating": "Medium",
                "min_investment": 500,
                "expense_ratio": 1.74
            },
            {
                "code": "AXIS_MIDCAP",
                "name": "Axis Midcap Fund",
                "description": "Targets mid-cap companies with sustainable competitive advantages.",
                "risk_rating": "Medium",
                "min_investment": 500,
                "expense_ratio": 1.71
            },
            {
                "code": "DSP_MIDCAP",
                "name": "DSP Midcap Fund",
                "description": "Invests in quality mid-cap companies with long-term growth potential.",
                "risk_rating": "Medium",
                "min_investment": 500,
                "expense_ratio": 1.67
            },
            {
                "code": "INVESCO_MIDCAP",
                "name": "Invesco India Mid Cap Fund",
                "description": "Focuses on mid-cap companies with strong fundamentals and growth prospects.",
                "risk_rating": "Medium-High",
                "min_investment": 1000,
                "expense_ratio": 1.97
            }
        ],
        "Small Cap": [
            {
                "code": "NIPPON_SMALL_CAP",
                "name": "Nippon India Small Cap Fund",
                "description": "Invests in small-cap companies with high growth potential.",
                "risk_rating": "High",
                "min_investment": 100,
                "expense_ratio": 1.88
            },
            {
                "code": "SBI_SMALL_CAP",
                "name": "SBI Small Cap Fund",
                "description": "Focuses on small companies with strong business models and growth prospects.",
                "risk_rating": "High",
                "min_investment": 500,
                "expense_ratio": 1.79
            },
            {
                "code": "AXIS_SMALL_CAP",
                "name": "Axis Small Cap Fund",
                "description": "Invests in small-cap companies with potential for capital appreciation.",
                "risk_rating": "High",
                "min_investment": 500,
                "expense_ratio": 1.95
            },
            {
                "code": "KOTAK_SMALL_CAP",
                "name": "Kotak Small Cap Fund",
                "description": "Targets promising small-cap companies across sectors.",
                "risk_rating": "High",
                "min_investment": 500,
                "expense_ratio": 1.91
            },
            {
                "code": "HDFC_SMALL_CAP",
                "name": "HDFC Small Cap Fund",
                "description": "Invests in small-cap companies with growth potential and reasonable valuations.",
                "risk_rating": "High",
                "min_investment": 500,
                "expense_ratio": 1.94
            }
        ],
        "Gold": [
            {
                "code": "SBI_GOLD",
                "name": "SBI Gold Fund",
                "description": "Fund of Fund investing in gold ETFs, providing exposure to gold prices.",
                "risk_rating": "Medium",
                "min_investment": 500,
                "expense_ratio": 0.88
            },
            {
                "code": "AXIS_GOLD",
                "name": "Axis Gold Fund",
                "description": "Fund of Fund investing in Axis Gold ETF, tracking domestic gold prices.",
                "risk_rating": "Medium",
                "min_investment": 500,
                "expense_ratio": 0.92
            },
            {
                "code": "ICICI_GOLD",
                "name": "ICICI Prudential Regular Gold Savings Fund",
                "description": "Invests in units of ICICI Prudential Gold ETF for gold price exposure.",
                "risk_rating": "Medium",
                "min_investment": 100,
                "expense_ratio": 1.02
            },
            {
                "code": "INVESCO_GOLD",
                "name": "Invesco India Gold Fund",
                "description": "Fund of Fund investing in Invesco India Gold ETF.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 0.95
            },
            {
                "code": "KOTAK_GOLD",
                "name": "Kotak Gold Fund",
                "description": "Fund of Fund investing in Kotak Gold ETF for gold exposure.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 0.96
            }
        ],
        "ETFs/Crypto": [
            {
                "code": "UTI_NIFTY_INDEX",
                "name": "UTI Nifty Index Fund",
                "description": "Index fund tracking the Nifty 50 index for broad market exposure.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 0.17
            },
            {
                "code": "HDFC_INDEX_SENSEX",
                "name": "HDFC Index Fund-SENSEX Plan",
                "description": "Index fund tracking the SENSEX, India's benchmark index for broad market exposure.",
                "risk_rating": "Medium",
                "min_investment": 100,
                "expense_ratio": 0.2
            },
            {
                "code": "MOTILAL_NASDAQ_100",
                "name": "Motilal Oswal Nasdaq 100 FOF",
                "description": "Fund of Fund investing in the Nasdaq 100 ETF, providing exposure to US tech stocks.",
                "risk_rating": "Medium-High",
                "min_investment": 500,
                "expense_ratio": 0.55
            },
            {
                "code": "ICICI_NIFTY_NEXT_50",
                "name": "ICICI Prudential Nifty Next 50 Index Fund",
                "description": "Index fund tracking the Nifty Next 50 index for exposure to emerging large-caps.",
                "risk_rating": "Medium-High",
                "min_investment": 1000,
                "expense_ratio": 0.41
            },
            {
                "code": "NIPPON_INDEX_SENSEX",
                "name": "Nippon India Index Fund - Sensex Plan",
                "description": "Index fund replicating the SENSEX index for passive investing.",
                "risk_rating": "Medium",
                "min_investment": 100,
                "expense_ratio": 0.31
            }
        ],
        "Other": [
            {
                "code": "AXIS_FOCUSED_25",
                "name": "Axis Focused 25 Fund",
                "description": "Concentrated portfolio of up to 25 stocks across market caps.",
                "risk_rating": "Medium-High",
                "min_investment": 500,
                "expense_ratio": 1.79
            },
            {
                "code": "ICICI_BALANCED_ADVANTAGE",
                "name": "ICICI Prudential Balanced Advantage Fund",
                "description": "Dynamic asset allocation fund that adjusts equity exposure based on market conditions.",
                "risk_rating": "Medium",
                "min_investment": 100,
                "expense_ratio": 1.66
            },
            {
                "code": "HDFC_HYBRID_EQUITY",
                "name": "HDFC Hybrid Equity Fund",
                "description": "Balanced fund investing in a mix of equity and debt instruments.",
                "risk_rating": "Medium",
                "min_investment": 5000,
                "expense_ratio": 1.84
            },
            {
                "code": "SBI_EQUITY_HYBRID",
                "name": "SBI Equity Hybrid Fund",
                "description": "Balanced fund with investments in equity and fixed income securities.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 1.76
            },
            {
                "code": "PARAG_FLEXI_CAP",
                "name": "Parag Parikh Flexi Cap Fund",
                "description": "Invests across market caps and geographies with a value investing approach.",
                "risk_rating": "Medium",
                "min_investment": 1000,
                "expense_ratio": 1.52
            }
        ]
    }
    
    # Only return Indian SIP suggestions
    return india_sip_suggestions.get(category, [])
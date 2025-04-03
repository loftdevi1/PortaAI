class SESSION_KEYS:
    NAVIGATION_INDEX = "navigation_index"
    RISK_PROFILE = "risk_profile"
    PORTFOLIO = "portfolio"
    ANALYSIS_RESULT = "analysis_result"
    RECOMMENDATIONS = "recommendations"
    SELECTED_CATEGORY = "selected_category"
    SELECTED_STOCKS = "selected_stocks"
    SELECTED_SIPS = "selected_sips"
    MARKET = "market"
    
    # Financial goals related keys
    FINANCIAL_GOALS = "financial_goals"
    CURRENT_GOAL_ID = "current_goal_id"
    CURRENT_GOAL_NAME = "current_goal_name"
    
    # Price alerts related keys
    PRICE_ALERTS = "price_alerts"
    CURRENT_ALERT_ID = "current_alert_id"
    
    # Database related keys
    USER_ID = "user_id"
    USER_NAME = "user_name"
    USER_EMAIL = "user_email"
    IS_LOGGED_IN = "is_logged_in"
    CURRENT_PORTFOLIO_ID = "current_portfolio_id"
    CURRENT_PORTFOLIO_NAME = "current_portfolio_name"
    USER_PORTFOLIOS = "user_portfolios"

def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """
    # Navigation and UI state
    if SESSION_KEYS.NAVIGATION_INDEX not in st.session_state:
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
    
    if SESSION_KEYS.RISK_PROFILE not in st.session_state:
        st.session_state[SESSION_KEYS.RISK_PROFILE] = ""
    
    if SESSION_KEYS.PORTFOLIO not in st.session_state:
        st.session_state[SESSION_KEYS.PORTFOLIO] = []
    
    if SESSION_KEYS.ANALYSIS_RESULT not in st.session_state:
        st.session_state[SESSION_KEYS.ANALYSIS_RESULT] = None
    
    if SESSION_KEYS.RECOMMENDATIONS not in st.session_state:
        st.session_state[SESSION_KEYS.RECOMMENDATIONS] = None
    
    if SESSION_KEYS.SELECTED_CATEGORY not in st.session_state:
        st.session_state[SESSION_KEYS.SELECTED_CATEGORY] = None
    
    if SESSION_KEYS.SELECTED_STOCKS not in st.session_state:
        st.session_state[SESSION_KEYS.SELECTED_STOCKS] = {}
        
    if SESSION_KEYS.SELECTED_SIPS not in st.session_state:
        st.session_state[SESSION_KEYS.SELECTED_SIPS] = {}
        
    if SESSION_KEYS.MARKET not in st.session_state:
        st.session_state[SESSION_KEYS.MARKET] = "INDIA"
    
    # User and authentication state
    if SESSION_KEYS.USER_ID not in st.session_state:
        st.session_state[SESSION_KEYS.USER_ID] = None
        
    if SESSION_KEYS.USER_NAME not in st.session_state:
        st.session_state[SESSION_KEYS.USER_NAME] = None
        
    if SESSION_KEYS.USER_EMAIL not in st.session_state:
        st.session_state[SESSION_KEYS.USER_EMAIL] = None
        
    if SESSION_KEYS.IS_LOGGED_IN not in st.session_state:
        st.session_state[SESSION_KEYS.IS_LOGGED_IN] = False
        
    # Portfolio database state
    if SESSION_KEYS.CURRENT_PORTFOLIO_ID not in st.session_state:
        st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID] = None
        
    if SESSION_KEYS.CURRENT_PORTFOLIO_NAME not in st.session_state:
        st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_NAME] = None
        
    if SESSION_KEYS.USER_PORTFOLIOS not in st.session_state:
        st.session_state[SESSION_KEYS.USER_PORTFOLIOS] = []
    
    # Financial goals state
    if SESSION_KEYS.FINANCIAL_GOALS not in st.session_state:
        st.session_state[SESSION_KEYS.FINANCIAL_GOALS] = []
        
    if SESSION_KEYS.CURRENT_GOAL_ID not in st.session_state:
        st.session_state[SESSION_KEYS.CURRENT_GOAL_ID] = None
        
    if SESSION_KEYS.CURRENT_GOAL_NAME not in st.session_state:
        st.session_state[SESSION_KEYS.CURRENT_GOAL_NAME] = None
        
    # Price alerts state
    if SESSION_KEYS.PRICE_ALERTS not in st.session_state:
        st.session_state[SESSION_KEYS.PRICE_ALERTS] = []
        
    if SESSION_KEYS.CURRENT_ALERT_ID not in st.session_state:
        st.session_state[SESSION_KEYS.CURRENT_ALERT_ID] = None

def get_risk_profile_allocation(risk_profile):
    """
    Get the recommended asset allocation based on risk profile.
    
    Args:
        risk_profile (str): Selected risk profile
        
    Returns:
        dict: Recommended allocation percentages by category
    """
    allocations = {
        "Low Risk (Conservative)": {
            "Large Cap": 40,
            "Mid Cap": 25,
            "Small Cap": 20,
            "Gold": 10,
            "ETFs/Crypto": 5
        },
        "Medium Risk (Balanced)": {
            "Large Cap": 30,
            "Mid Cap": 30,
            "Small Cap": 25,
            "Gold": 10,
            "ETFs/Crypto": 5
        },
        "High Risk (Aggressive)": {
            "Large Cap": 25,
            "Mid Cap": 25,
            "Small Cap": 35,
            "ETFs/Crypto": 10,
            "Gold": 5
        }
    }
    
    return allocations.get(risk_profile, allocations["Medium Risk (Balanced)"])

def get_asset_category_color():
    """
    Get consistent colors for asset categories for visualization.
    
    Returns:
        dict: Color mapping for asset categories
    """
    return {
        "Large Cap": "#1f77b4",
        "Mid Cap": "#ff7f0e",
        "Small Cap": "#2ca02c",
        "Gold": "#d62728",
        "ETFs/Crypto": "#9467bd",
        "Other": "#8c564b"
    }

# Import streamlit for the initialize function
import streamlit as st
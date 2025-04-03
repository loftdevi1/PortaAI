class SESSION_KEYS:
    NAVIGATION_INDEX = "navigation_index"
    RISK_PROFILE = "risk_profile"
    PORTFOLIO = "portfolio"
    ANALYSIS_RESULT = "analysis_result"
    RECOMMENDATIONS = "recommendations"
    SELECTED_CATEGORY = "selected_category"
    SELECTED_STOCKS = "selected_stocks"

def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """
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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import datetime
import os
from utils import SESSION_KEYS, initialize_session_state, get_risk_profile_allocation, get_asset_category_color
from portfolio_analyzer import analyze_portfolio, get_allocation_recommendation
from stock_service import get_stock_suggestions, fetch_stock_data, get_sip_suggestions
import database as db
import goals as goal_utils
from price_alerts import create_price_alert, get_user_price_alerts, delete_price_alert, check_price_alerts, send_sms_price_alerts

def main():
    # Set up page configuration
    st.set_page_config(
        page_title="PortaAi - Portfolio Balancing",
        page_icon="💼",
        layout="wide"
    )
    
    # Initialize session state values
    initialize_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("PortaAi")
        st.subheader("Portfolio Balancing Tool")
        
        # Market selection (India or US)
        market = st.radio(
            "Select Market",
            ["INDIA", "US"],
            index=0 if st.session_state[SESSION_KEYS.MARKET] == "INDIA" else 1
        )
        st.session_state[SESSION_KEYS.MARKET] = market
        
        # Show navigation options based on authentication and profile status
        if st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
            # Navigation for logged-in users
            if st.session_state[SESSION_KEYS.RISK_PROFILE]:
                # Full navigation if risk profile is set
                navigation = st.radio(
                    "Navigation",
                    ["Welcome", "Risk Profile", "Portfolio Input", "Portfolio Analysis", 
                     "Recommendations", "Stock Selection", "Summary", "Portfolio Management", "Financial Goals", "Price Alerts"],
                    index=st.session_state[SESSION_KEYS.NAVIGATION_INDEX]
                )
                
                # Update navigation state based on selection
                nav_options = ["Welcome", "Risk Profile", "Portfolio Input", "Portfolio Analysis", 
                              "Recommendations", "Stock Selection", "Summary", "Portfolio Management", "Financial Goals", "Price Alerts"]
                st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = nav_options.index(navigation)
            else:
                # Limited navigation if no risk profile yet
                navigation = st.radio(
                    "Navigation",
                    ["Welcome", "Risk Profile", "Portfolio Management"],
                    index=st.session_state[SESSION_KEYS.NAVIGATION_INDEX]
                )
                
                # Make sure the index matches the selection
                if navigation == "Welcome":
                    st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
                elif navigation == "Risk Profile":
                    st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 1
                elif navigation == "Portfolio Management":
                    st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 7
            
            # Logout option for logged-in users
            if st.button("Logout"):
                # Reset user session state
                st.session_state[SESSION_KEYS.IS_LOGGED_IN] = False
                st.session_state[SESSION_KEYS.USER_ID] = None
                st.session_state[SESSION_KEYS.USER_NAME] = None
                st.session_state[SESSION_KEYS.USER_EMAIL] = None
                st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID] = None
                st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_NAME] = None
                st.session_state[SESSION_KEYS.USER_PORTFOLIOS] = []
                st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
                st.rerun()
        else:
            # Navigation for non-logged in users
            if st.session_state[SESSION_KEYS.RISK_PROFILE]:
                navigation = st.radio(
                    "Navigation",
                    ["Welcome", "Risk Profile", "Portfolio Input", "Portfolio Analysis", 
                     "Recommendations", "Stock Selection", "Summary"],
                    index=st.session_state[SESSION_KEYS.NAVIGATION_INDEX]
                )
                
                # Update navigation state based on selection
                nav_options = ["Welcome", "Risk Profile", "Portfolio Input", "Portfolio Analysis", 
                              "Recommendations", "Stock Selection", "Summary"]
                st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = nav_options.index(navigation)
            else:
                navigation = st.radio(
                    "Navigation",
                    ["Welcome", "Risk Profile"],
                    index=st.session_state[SESSION_KEYS.NAVIGATION_INDEX]
                )
    
    # Display login/register screens if not logged in
    if not st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
        # Navigation between login and register for non-logged in users
        auth_nav = st.sidebar.radio(
            "Authentication",
            ["Login", "Register"],
            index=0
        )
        
        if auth_nav == "Login":
            show_login_screen()
        else:
            show_register_screen()
    else:
        # For logged in users, show regular navigation
        # Display the appropriate screen based on navigation
        if st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 0:
            show_welcome_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 1:
            show_risk_profile_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 2:
            show_portfolio_input_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 3:
            show_portfolio_analysis_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 4:
            show_recommendations_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 5:
            show_stock_selection_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 6:
            show_summary_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 7:
            show_portfolio_management_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 8:
            show_financial_goals_screen()
        elif st.session_state[SESSION_KEYS.NAVIGATION_INDEX] == 9:
            show_price_alerts_screen()

def show_welcome_screen():
    st.title("Welcome to PortaAi")
    
    st.markdown("""
    ### Your Personal Portfolio Balancing Assistant
    
    PortaAi helps you balance your stock portfolio according to your risk tolerance.
    
    **What we offer:**
    - Portfolio analysis based on your risk profile
    - Visual representation of your current allocation
    - Recommendations for balanced distribution
    - Personalized stock and SIP suggestions
    - Support for both Indian and US markets
    """)
    
    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Get Started", use_container_width=True):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 1
            st.rerun()

def show_risk_profile_screen():
    st.title("Select Your Risk Strategy")
    
    st.markdown("""
    ### What's your investment risk tolerance?
    
    Select the risk profile that best matches your investment goals and comfort level.
    """)
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        risk_profiles = {
            "Low Risk (Conservative)": """
                - Focus on capital preservation
                - Stable, consistent returns
                - Lower volatility
                - Suitable for short-term goals or retirement
            """,
            "Medium Risk (Balanced)": """
                - Balance between growth and safety
                - Moderate volatility
                - Suitable for medium-term goals
            """,
            "High Risk (Aggressive)": """
                - Focus on capital appreciation
                - Higher volatility
                - Potentially higher returns
                - Suitable for long-term goals
            """
        }
        
        selected_risk = st.radio(
            "Select your risk tolerance:",
            list(risk_profiles.keys()),
            index=0 if st.session_state[SESSION_KEYS.RISK_PROFILE] == "" else 
                  list(risk_profiles.keys()).index(st.session_state[SESSION_KEYS.RISK_PROFILE])
        )
        
        st.markdown(risk_profiles[selected_risk])
    
    with col2:
        # Show allocation pie chart based on risk profile
        if selected_risk:
            fig = px.pie(
                names=list(get_risk_profile_allocation(selected_risk).keys()),
                values=list(get_risk_profile_allocation(selected_risk).values()),
                title=f"Recommended Allocation",
                color=list(get_risk_profile_allocation(selected_risk).keys()),
                color_discrete_map=get_asset_category_color()
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if st.button("Next", use_container_width=True):
        st.session_state[SESSION_KEYS.RISK_PROFILE] = selected_risk
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 2
        st.rerun()

def show_portfolio_input_screen():
    st.title("Current Portfolio Input")
    
    st.markdown("""
    ### Enter your current investments
    
    Add your existing stocks, SIPs and other investments to analyze your portfolio.
    """)
    
    # Initialize portfolio in session if not exists
    if SESSION_KEYS.PORTFOLIO not in st.session_state:
        st.session_state[SESSION_KEYS.PORTFOLIO] = []
    
    # Display current portfolio items if any
    if st.session_state[SESSION_KEYS.PORTFOLIO]:
        st.subheader("Your Current Portfolio")
        df = pd.DataFrame(st.session_state[SESSION_KEYS.PORTFOLIO])
        st.dataframe(df)
        
        # Calculate total investment
        total_investment = sum(item['amount'] for item in st.session_state[SESSION_KEYS.PORTFOLIO])
        st.info(f"Total Investment: ${total_investment:,.2f}")
    
    # Create tabs for Stock and SIP input
    tab1, tab2 = st.tabs(["Stock/ETF Input", "SIP Input"])
    
    with tab1:
        # Form for adding new stock
        with st.form("add_stock_form"):
            st.subheader("Add Stock/ETF Investment")
            
            col1, col2 = st.columns(2)
            
            with col1:
                stock_name = st.text_input("Stock/ETF Name")
            
            with col2:
                stock_category = st.selectbox(
                    "Category",
                    ["Large Cap", "Mid Cap", "Small Cap", "Gold", "ETFs/Crypto", "Other"]
                )
            
            investment_amount = st.number_input("Investment Amount ($)", min_value=0.0, step=100.0)
            
            submitted = st.form_submit_button("Add to Portfolio")
            
            if submitted and stock_name and investment_amount > 0:
                # Add to portfolio
                st.session_state[SESSION_KEYS.PORTFOLIO].append({
                    "name": stock_name,
                    "category": stock_category,
                    "amount": investment_amount,
                    "type": "Stock/ETF"
                })
                st.rerun()
    
    with tab2:
        # Form for adding new SIP
        with st.form("add_sip_form"):
            st.subheader("Add SIP Investment")
            
            col1, col2 = st.columns(2)
            
            with col1:
                sip_name = st.text_input("SIP/Mutual Fund Name")
            
            with col2:
                sip_category = st.selectbox(
                    "SIP Category",
                    ["Large Cap", "Mid Cap", "Small Cap", "Gold", "ETFs/Crypto", "Other"]
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_amount = st.number_input("Monthly SIP Amount ($)", min_value=0.0, step=50.0)
            
            with col2:
                months_invested = st.number_input("Months Invested So Far", min_value=0, step=1)
            
            # Calculate total invested amount
            total_sip_amount = monthly_amount * months_invested
            
            if monthly_amount > 0 and months_invested > 0:
                st.write(f"Total SIP Investment: ${total_sip_amount:,.2f}")
            
            submitted_sip = st.form_submit_button("Add SIP to Portfolio")
            
            if submitted_sip and sip_name and total_sip_amount > 0:
                # Add to portfolio
                st.session_state[SESSION_KEYS.PORTFOLIO].append({
                    "name": sip_name,
                    "category": sip_category,
                    "amount": total_sip_amount,
                    "monthly_amount": monthly_amount,
                    "months_invested": months_invested,
                    "type": "SIP"
                })
                st.rerun()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Portfolio", use_container_width=True):
            st.session_state[SESSION_KEYS.PORTFOLIO] = []
            st.rerun()
    
    with col2:
        # Only show save button if user is logged in and has a current portfolio
        if st.session_state[SESSION_KEYS.IS_LOGGED_IN] and st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID]:
            if st.button("Save Portfolio", use_container_width=True, disabled=len(st.session_state[SESSION_KEYS.PORTFOLIO]) == 0):
                if save_current_portfolio_to_database():
                    st.success("Portfolio saved successfully!")
                    st.rerun()
    
    with col3:
        # Only allow proceeding if portfolio has items
        if st.button("Analyze Portfolio", use_container_width=True, disabled=len(st.session_state[SESSION_KEYS.PORTFOLIO]) == 0):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 3
            st.rerun()

def show_portfolio_analysis_screen():
    st.title("Portfolio Analysis")
    
    # Make sure we have portfolio data
    if not st.session_state[SESSION_KEYS.PORTFOLIO]:
        st.warning("No portfolio data available. Please go back and add your investments.")
        if st.button("Back to Portfolio Input"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 2
            st.rerun()
        return
    
    # Analyze the portfolio
    analysis_result = analyze_portfolio(
        st.session_state[SESSION_KEYS.PORTFOLIO],
        st.session_state[SESSION_KEYS.RISK_PROFILE]
    )
    
    st.session_state[SESSION_KEYS.ANALYSIS_RESULT] = analysis_result
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Allocation")
        
        # Create pie chart for current allocation
        fig = px.pie(
            names=list(analysis_result["current_allocation"].keys()),
            values=list(analysis_result["current_allocation"].values()),
            title="Current Portfolio Distribution",
            color=list(analysis_result["current_allocation"].keys()),
            color_discrete_map=get_asset_category_color()
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Target Allocation")
        
        # Create pie chart for target allocation
        fig = px.pie(
            names=list(analysis_result["target_allocation"].keys()),
            values=list(analysis_result["target_allocation"].values()),
            title=f"Target Allocation for {st.session_state[SESSION_KEYS.RISK_PROFILE]}",
            color=list(analysis_result["target_allocation"].keys()),
            color_discrete_map=get_asset_category_color()
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Display imbalance insights
    st.subheader("Portfolio Insights")
    
    for insight in analysis_result["insights"]:
        if insight["type"] == "warning":
            st.warning(insight["message"])
        elif insight["type"] == "info":
            st.info(insight["message"])
        else:
            st.success(insight["message"])
    
    if st.button("Get Recommendations", use_container_width=True):
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 4
        st.rerun()

def show_recommendations_screen():
    st.title("Investment Distribution Recommendations")
    
    if not st.session_state[SESSION_KEYS.ANALYSIS_RESULT]:
        st.warning("No analysis data available. Please go back and analyze your portfolio.")
        if st.button("Back to Analysis"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 3
            st.rerun()
        return
    
    # Get rebalance recommendations
    recommendations = get_allocation_recommendation(
        st.session_state[SESSION_KEYS.PORTFOLIO],
        st.session_state[SESSION_KEYS.ANALYSIS_RESULT]
    )
    
    st.session_state[SESSION_KEYS.RECOMMENDATIONS] = recommendations
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recommended Adjustments")
        
        if recommendations["actions"]:
            for action in recommendations["actions"]:
                if action["action_type"] == "increase":
                    st.success(f"**{action['category']}**: {action['message']}")
                elif action["action_type"] == "decrease":
                    st.warning(f"**{action['category']}**: {action['message']}")
                else:
                    st.info(f"**{action['category']}**: {action['message']}")
        else:
            st.success("Your portfolio is well-balanced! No adjustments needed.")
    
    with col2:
        st.subheader("Recommended Distribution")
        
        # Create recommended distribution chart
        total_portfolio = sum(item['amount'] for item in st.session_state[SESSION_KEYS.PORTFOLIO])
        recommended_values = []
        recommended_labels = []
        
        target_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"]
        
        for category, percentage in target_allocation.items():
            value = total_portfolio * (percentage / 100)
            recommended_values.append(value)
            recommended_labels.append(f"{category} (${value:,.2f})")
        
        fig = px.pie(
            names=recommended_labels,
            values=recommended_values,
            title="Recommended Investment Distribution",
            color=list(target_allocation.keys()),
            color_discrete_map=get_asset_category_color()
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Category selection for specific stocks
    st.subheader("Select a category to view investment recommendations")
    
    categories = list(st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"].keys())
    selected_category = st.selectbox("Category", categories)
    
    if selected_category:
        st.session_state[SESSION_KEYS.SELECTED_CATEGORY] = selected_category
    
    if st.button("View Investment Recommendations", use_container_width=True):
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 5
        st.rerun()

def show_stock_selection_screen():
    st.title("Investment Selection")
    
    if not st.session_state.get(SESSION_KEYS.SELECTED_CATEGORY):
        st.warning("No category selected. Please go back and select a category.")
        if st.button("Back to Recommendations"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 4
            st.rerun()
        return
    
    selected_category = st.session_state[SESSION_KEYS.SELECTED_CATEGORY]
    market = st.session_state[SESSION_KEYS.MARKET]
    
    # Create tabs for stocks and SIPs
    tab1, tab2 = st.tabs([f"{selected_category} Stocks/ETFs", f"{selected_category} SIPs"])
    
    with tab1:
        st.subheader(f"Recommended {selected_category} Stocks/ETFs")
        
        # Get stock suggestions for the selected category
        suggested_stocks = get_stock_suggestions(selected_category, market)
        
        # Initialize selected stocks if not already in session
        if SESSION_KEYS.SELECTED_STOCKS not in st.session_state:
            st.session_state[SESSION_KEYS.SELECTED_STOCKS] = {}
        
        # Make sure the category exists in selected stocks
        if selected_category not in st.session_state[SESSION_KEYS.SELECTED_STOCKS]:
            st.session_state[SESSION_KEYS.SELECTED_STOCKS][selected_category] = []
        
        # Get stock data
        if suggested_stocks:
            ticker_data = fetch_stock_data([stock['ticker'] for stock in suggested_stocks])
            
            # Display the stock choices
            stock_selections = []
            
            for stock in suggested_stocks:
                ticker = stock['ticker']
                data = ticker_data.get(ticker, {})
                
                # Check if already selected
                is_selected = any(s['ticker'] == ticker for s in st.session_state[SESSION_KEYS.SELECTED_STOCKS].get(selected_category, []))
                
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{stock['name']} ({ticker})**")
                    st.write(stock['description'])
                
                with col2:
                    if data:
                        st.write(f"Current Price: ${data.get('current_price', 'N/A')}")
                        change = data.get('price_change_percent', 0)
                        if change > 0:
                            st.write(f"Change: 📈 +{change:.2f}%")
                        else:
                            st.write(f"Change: 📉 {change:.2f}%")
                    else:
                        st.write("Price data unavailable")
                
                with col3:
                    # Calculate the risk rating based on volatility or other factors
                    risk_rating = stock.get('risk_rating', 'Medium')
                    st.write(f"Risk: {risk_rating}")
                
                with col4:
                    selected = st.checkbox("Select", value=is_selected, key=f"select_{ticker}")
                    
                    if selected:
                        if not is_selected:
                            # Add to selected stocks
                            st.session_state[SESSION_KEYS.SELECTED_STOCKS][selected_category].append({
                                'ticker': ticker,
                                'name': stock['name'],
                                'price': data.get('current_price', 0) if data else 0
                            })
                    else:
                        if is_selected:
                            # Remove from selected stocks
                            st.session_state[SESSION_KEYS.SELECTED_STOCKS][selected_category] = [
                                s for s in st.session_state[SESSION_KEYS.SELECTED_STOCKS][selected_category]
                                if s['ticker'] != ticker
                            ]
                
                st.markdown("---")
        else:
            st.info(f"No stock suggestions available for {selected_category} in the {market} market.")
    
    with tab2:
        st.subheader(f"Recommended {selected_category} SIPs")
        
        # Get SIP suggestions for the selected category
        suggested_sips = get_sip_suggestions(selected_category, market)
        
        # Initialize selected SIPs if not already in session
        if SESSION_KEYS.SELECTED_SIPS not in st.session_state:
            st.session_state[SESSION_KEYS.SELECTED_SIPS] = {}
        
        # Make sure the category exists in selected SIPs
        if selected_category not in st.session_state[SESSION_KEYS.SELECTED_SIPS]:
            st.session_state[SESSION_KEYS.SELECTED_SIPS][selected_category] = []
        
        # Display the SIP choices
        if suggested_sips:
            for sip in suggested_sips:
                code = sip['code']
                
                # Check if already selected
                is_selected = any(s['code'] == code for s in st.session_state[SESSION_KEYS.SELECTED_SIPS].get(selected_category, []))
                
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{sip['name']} ({code})**")
                    st.write(sip['description'])
                
                with col2:
                    st.write(f"Min. Investment: ₹{sip['min_investment']}")
                    st.write(f"Expense Ratio: {sip['expense_ratio']}%")
                
                with col3:
                    # Risk rating
                    risk_rating = sip.get('risk_rating', 'Medium')
                    st.write(f"Risk: {risk_rating}")
                
                with col4:
                    selected = st.checkbox("Select", value=is_selected, key=f"select_sip_{code}")
                    
                    if selected:
                        if not is_selected:
                            # Add to selected SIPs
                            st.session_state[SESSION_KEYS.SELECTED_SIPS][selected_category].append({
                                'code': code,
                                'name': sip['name'],
                                'min_investment': sip['min_investment']
                            })
                    else:
                        if is_selected:
                            # Remove from selected SIPs
                            st.session_state[SESSION_KEYS.SELECTED_SIPS][selected_category] = [
                                s for s in st.session_state[SESSION_KEYS.SELECTED_SIPS][selected_category]
                                if s['code'] != code
                            ]
                
                st.markdown("---")
        else:
            st.info(f"No SIP suggestions available for {selected_category} in the {market} market.")
    
    # Continue button
    if st.button("Continue to Summary", use_container_width=True):
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 6
        st.rerun()

def show_summary_screen():
    st.title("Investment Summary")
    
    # Auto-save portfolio if the user is logged in and has a current portfolio
    if st.session_state[SESSION_KEYS.IS_LOGGED_IN] and st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID]:
        # Check if portfolio has any items before saving
        if st.session_state[SESSION_KEYS.PORTFOLIO]:
            save_successful = save_current_portfolio_to_database()
            if save_successful:
                st.success("Your portfolio has been automatically saved!")
    elif st.session_state[SESSION_KEYS.IS_LOGGED_IN] and not st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID]:
        # If logged in but no portfolio is selected, ask user to create one
        st.info("Create a portfolio in the Portfolio Management section to save your selections.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Selected Stocks/ETFs")
        
        selected_stocks_exists = False
        
        for category, stocks in st.session_state[SESSION_KEYS.SELECTED_STOCKS].items():
            if stocks:
                selected_stocks_exists = True
                st.write(f"**{category}**")
                
                for stock in stocks:
                    st.write(f"- {stock['name']} ({stock['ticker']})")
                
                st.markdown("---")
        
        if not selected_stocks_exists:
            st.info("No stocks/ETFs selected. Go back to select some stocks.")
    
    with col2:
        st.subheader("Selected SIPs")
        
        selected_sips_exists = False
        
        for category, sips in st.session_state[SESSION_KEYS.SELECTED_SIPS].items():
            if sips:
                selected_sips_exists = True
                st.write(f"**{category}**")
                
                for sip in sips:
                    st.write(f"- {sip['name']} (Min: ₹{sip['min_investment']})")
                
                st.markdown("---")
        
        if not selected_sips_exists:
            st.info("No SIPs selected. Go back to select some SIPs.")
    
    # Portfolio overview
    st.subheader("Portfolio Rebalancing Summary")
    
    if st.session_state[SESSION_KEYS.RECOMMENDATIONS]:
        recommendations = st.session_state[SESSION_KEYS.RECOMMENDATIONS]
        
        if recommendations["actions"]:
            for action in recommendations["actions"]:
                if action["action_type"] == "increase":
                    st.success(f"**{action['category']}**: {action['message']}")
                elif action["action_type"] == "decrease":
                    st.warning(f"**{action['category']}**: {action['message']}")
                else:
                    st.info(f"**{action['category']}**: {action['message']}")
        else:
            st.success("Your portfolio is well-balanced! No adjustments needed.")
    
    # Final notes and recommendations
    st.subheader("Next Steps")
    
    st.markdown("""
    ### Implementing Your Investment Plan:
    
    1. **For Stocks/ETFs:**
       - Open a brokerage account if you don't have one
       - Place orders for the selected stocks in the recommended proportions
       - Consider dollar-cost averaging for large investments
    
    2. **For SIPs:**
       - Set up systematic investment plans with the selected mutual funds
       - Choose a convenient date for monthly debits
       - Consider dividing your monthly investment across multiple funds
    
    3. **Portfolio Maintenance:**
       - Review your portfolio quarterly
       - Rebalance annually or when allocation drifts more than 5% from targets
       - Consider tax implications when selling investments
    """)
    
    # Download report option
    if st.button("Start Over", use_container_width=True):
        # Reset session state (keeping risk profile)
        risk_profile = st.session_state[SESSION_KEYS.RISK_PROFILE]
        market = st.session_state[SESSION_KEYS.MARKET]
        
        st.session_state[SESSION_KEYS.PORTFOLIO] = []
        st.session_state[SESSION_KEYS.ANALYSIS_RESULT] = None
        st.session_state[SESSION_KEYS.RECOMMENDATIONS] = None
        st.session_state[SESSION_KEYS.SELECTED_CATEGORY] = None
        st.session_state[SESSION_KEYS.SELECTED_STOCKS] = {}
        st.session_state[SESSION_KEYS.SELECTED_SIPS] = {}
        st.session_state[SESSION_KEYS.RISK_PROFILE] = risk_profile
        st.session_state[SESSION_KEYS.MARKET] = market
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
        
        st.rerun()

def show_login_screen():
    st.title("Login to PortaAi")
    
    st.markdown("""
    ### Welcome back to PortaAi
    
    Login to access your saved portfolios and continue your investment journey.
    """)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login")
        
        if submitted and username and password:
            # Hash the password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try to find the user
            user = db.get_user_by_username(username)
            
            if user and user.password_hash == hashed_password:
                # Login successful
                st.session_state[SESSION_KEYS.IS_LOGGED_IN] = True
                st.session_state[SESSION_KEYS.USER_ID] = user.id
                st.session_state[SESSION_KEYS.USER_NAME] = user.username
                st.session_state[SESSION_KEYS.USER_EMAIL] = user.email
                
                # Get user risk profile if already set
                if user.risk_profile:
                    st.session_state[SESSION_KEYS.RISK_PROFILE] = user.risk_profile
                
                # Load user portfolios
                portfolios = db.get_user_portfolios(user.id)
                st.session_state[SESSION_KEYS.USER_PORTFOLIOS] = portfolios
                
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown("---")
    st.markdown("Don't have an account? Use the sidebar to register.")

def show_register_screen():
    st.title("Create an Account")
    
    st.markdown("""
    ### Join PortaAi
    
    Create an account to save your portfolios and track your investments.
    """)
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # Validate the form
            if not username or not email or not password:
                st.error("All fields are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Check if username already exists
                existing_user = db.get_user_by_username(username)
                
                if existing_user:
                    st.error("Username already exists")
                else:
                    # Hash the password for storage
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    
                    try:
                        # Create the user
                        user_id = db.create_user(username, email, hashed_password)
                        
                        # Login the user
                        st.session_state[SESSION_KEYS.IS_LOGGED_IN] = True
                        st.session_state[SESSION_KEYS.USER_ID] = user_id
                        st.session_state[SESSION_KEYS.USER_NAME] = username
                        st.session_state[SESSION_KEYS.USER_EMAIL] = email
                        
                        st.success("Account created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating account: {str(e)}")
    
    st.markdown("---")
    st.markdown("Already have an account? Use the sidebar to login.")

def show_portfolio_management_screen():
    st.title("Portfolio Management")
    
    if not st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
        st.warning("Please login to manage your portfolios")
        return
    
    st.markdown(f"### Welcome, {st.session_state[SESSION_KEYS.USER_NAME]}")
    
    # Create tabs for different portfolio management functions
    tab1, tab2 = st.tabs(["My Portfolios", "Create New Portfolio"])
    
    with tab1:
        st.subheader("Your Saved Portfolios")
        
        # Refresh portfolios list
        portfolios = db.get_user_portfolios(st.session_state[SESSION_KEYS.USER_ID])
        st.session_state[SESSION_KEYS.USER_PORTFOLIOS] = portfolios
        
        if not portfolios:
            st.info("You don't have any saved portfolios yet. Create a new one to get started.")
        else:
            # Display portfolios in a table
            portfolio_data = []
            
            for portfolio in portfolios:
                # Get investments for this portfolio
                investments = db.get_portfolio_investments(portfolio.id)
                total_value = sum(investment.amount for investment in investments)
                
                portfolio_data.append({
                    "ID": portfolio.id,
                    "Name": portfolio.name,
                    "Description": portfolio.description or "-",
                    "Market": portfolio.market,
                    "Investments": len(investments),
                    "Total Value": f"${total_value:,.2f}",
                    "Created": portfolio.created_at.strftime("%Y-%m-%d")
                })
            
            df = pd.DataFrame(portfolio_data)
            st.dataframe(df, use_container_width=True)
            
            # Portfolio selection
            selected_portfolio_id = st.selectbox(
                "Select a portfolio to load",
                options=[p.id for p in portfolios],
                format_func=lambda x: next((p.name for p in portfolios if p.id == x), "")
            )
            
            if selected_portfolio_id:
                if st.button("Load Selected Portfolio"):
                    # Load the selected portfolio
                    load_portfolio_from_database(selected_portfolio_id)
                    st.success("Portfolio loaded successfully!")
                    st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 2  # Go to portfolio input screen
                    st.rerun()
                
                if st.button("Delete Selected Portfolio", type="secondary"):
                    # Delete confirmation
                    if st.checkbox("I understand this action cannot be undone"):
                        if db.delete_portfolio(selected_portfolio_id):
                            st.success("Portfolio deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete portfolio")
    
    with tab2:
        st.subheader("Create a New Portfolio")
        
        with st.form("create_portfolio_form"):
            portfolio_name = st.text_input("Portfolio Name")
            portfolio_description = st.text_area("Description (optional)")
            portfolio_market = st.radio("Market", ["INDIA", "US"])
            
            submitted = st.form_submit_button("Create Portfolio")
            
            if submitted and portfolio_name:
                try:
                    # Create the portfolio
                    portfolio_id = db.create_portfolio(
                        st.session_state[SESSION_KEYS.USER_ID],
                        portfolio_name,
                        portfolio_description,
                        portfolio_market
                    )
                    
                    # Set as current portfolio
                    st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID] = portfolio_id
                    st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_NAME] = portfolio_name
                    st.session_state[SESSION_KEYS.MARKET] = portfolio_market
                    
                    # Clear current portfolio data
                    st.session_state[SESSION_KEYS.PORTFOLIO] = []
                    
                    st.success("Portfolio created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating portfolio: {str(e)}")

def load_portfolio_from_database(portfolio_id):
    """Load a portfolio from the database into the session state"""
    portfolio = db.get_portfolio_by_id(portfolio_id)
    
    if not portfolio:
        st.error("Portfolio not found")
        return False
    
    # Set portfolio info in session
    st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID] = portfolio.id
    st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_NAME] = portfolio.name
    st.session_state[SESSION_KEYS.MARKET] = portfolio.market
    
    # Get investments
    investments = db.get_portfolio_investments(portfolio.id)
    
    # Clear current portfolio and load from database
    portfolio_items = []
    
    for inv in investments:
        item = {
            "name": inv.name,
            "category": inv.category,
            "amount": inv.amount,
            "type": inv.investment_type
        }
        
        # Add SIP-specific fields if applicable
        if inv.investment_type == "SIP" and inv.monthly_amount and inv.months_invested:
            item["monthly_amount"] = inv.monthly_amount
            item["months_invested"] = inv.months_invested
        
        # Add ticker if available
        if inv.ticker:
            item["ticker"] = inv.ticker
            
        portfolio_items.append(item)
    
    st.session_state[SESSION_KEYS.PORTFOLIO] = portfolio_items
    
    # Get user risk profile if not already set
    if not st.session_state[SESSION_KEYS.RISK_PROFILE]:
        user = db.get_user_by_id(st.session_state[SESSION_KEYS.USER_ID])
        if user and user.risk_profile:
            st.session_state[SESSION_KEYS.RISK_PROFILE] = user.risk_profile
    
    return True

def show_financial_goals_screen():
    """
    Display the financial goals screen where users can create and track their financial goals
    """
    st.title("Financial Goals Planning")
    
    # Check if user is logged in
    if not st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
        st.warning("Please login to use the financial goals feature")
        if st.button("Go to Login"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
            st.rerun()
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["My Goals", "Create New Goal", "Goal-Based Portfolio"])
    
    with tab1:
        st.subheader("Your Financial Goals")
        
        # Fetch user's goals
        user_id = st.session_state[SESSION_KEYS.USER_ID]
        user_goals = goal_utils.get_user_goals(user_id)
        
        if not user_goals:
            st.info("You don't have any financial goals yet. Create one to get started!")
        else:
            # Display each goal as a card with progress
            for goal in user_goals:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Calculate progress percentage
                    progress = goal_utils.calculate_goal_progress_percentage(goal.current_amount, goal.target_amount)
                    
                    # Calculate remaining time
                    now = datetime.datetime.utcnow()
                    days_remaining = (goal.target_date - now).days
                    years_remaining = max(0, days_remaining / 365)
                    
                    # Create an expander for each goal
                    with st.expander(f"**{goal.name}** - ${goal.target_amount:,.2f}", expanded=True):
                        st.markdown(f"**Description:** {goal.description}")
                        st.markdown(f"**Target Date:** {goal.target_date.strftime('%b %d, %Y')} ({days_remaining} days remaining)")
                        st.markdown(f"**Risk Level:** {goal.risk_level}")
                        
                        # Progress bar
                        st.progress(progress / 100)
                        st.markdown(f"**Progress:** ${goal.current_amount:,.2f} of ${goal.target_amount:,.2f} ({progress:.1f}%)")
                        
                        # Monthly investment required
                        expected_return = goal_utils.get_expected_return_rate(goal.risk_level)
                        monthly_needed = goal_utils.calculate_monthly_investment_needed(
                            goal.target_amount, goal.current_amount, years_remaining, expected_return
                        )
                        
                        st.markdown(f"**Suggested Monthly Investment:** ${monthly_needed:,.2f}")
                        
                        # Update progress form
                        with st.form(key=f"update_goal_{goal.id}"):
                            new_amount = st.number_input("Current Amount", 
                                                        min_value=0.0, 
                                                        value=float(goal.current_amount),
                                                        step=100.0)
                            
                            update_submitted = st.form_submit_button("Update Progress")
                            if update_submitted:
                                if goal_utils.update_goal_progress(goal.id, new_amount):
                                    st.success("Goal progress updated!")
                                    st.rerun()
                
                with col2:
                    # Delete goal button
                    if st.button("Delete", key=f"delete_{goal.id}"):
                        if goal_utils.delete_goal(goal.id):
                            st.success("Goal deleted successfully!")
                            st.rerun()
    
    with tab2:
        st.subheader("Create a New Financial Goal")
        
        with st.form("create_goal_form"):
            goal_name = st.text_input("Goal Name", placeholder="e.g., Retirement, Home Purchase, Education")
            
            goal_description = st.text_area("Description", placeholder="Describe your financial goal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                target_amount = st.number_input("Target Amount ($)", min_value=1000.0, step=1000.0)
            
            with col2:
                timeline_years = st.number_input("Timeline (Years)", min_value=1, step=1)
            
            risk_level = st.select_slider(
                "Risk Level",
                options=["Low", "Medium", "High"],
                value="Medium"
            )
            
            create_goal = st.form_submit_button("Create Goal")
            
            if create_goal and goal_name and target_amount > 0 and timeline_years > 0:
                user_id = st.session_state[SESSION_KEYS.USER_ID]
                try:
                    goal_id = goal_utils.create_financial_goal(
                        user_id=user_id,
                        name=goal_name,
                        description=goal_description,
                        target_amount=target_amount,
                        timeline_years=timeline_years,
                        risk_level=risk_level
                    )
                    if goal_id:
                        st.success("Financial goal created successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error creating goal: {e}")
    
    with tab3:
        st.subheader("Goal-Based Portfolio Planning")
        
        # Get user's goals for selection
        user_id = st.session_state[SESSION_KEYS.USER_ID]
        user_goals = goal_utils.get_user_goals(user_id)
        
        if not user_goals:
            st.warning("You don't have any financial goals yet. Create a goal first to use this feature.")
            if st.button("Create a New Goal"):
                # Switch to the Create New Goal tab
                st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 3
                st.rerun()
        else:
            # Goal selection
            goal_options = {f"{goal.name} (${goal.target_amount:,.0f}, {goal.timeline_years} years)": goal.id for goal in user_goals}
            selected_goal_label = st.selectbox("Choose a financial goal", list(goal_options.keys()))
            selected_goal_id = goal_options[selected_goal_label]
            
            # Retrieve the selected goal
            selected_goal = goal_utils.get_goal_by_id(selected_goal_id)
            
            if selected_goal:
                # Display goal details
                st.write("---")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader(f"Goal: {selected_goal.name}")
                    st.markdown(f"**Target amount:** ${selected_goal.target_amount:,.2f}")
                    st.markdown(f"**Timeline:** {selected_goal.timeline_years} years")
                
                with col2:
                    progress = goal_utils.calculate_goal_progress_percentage(selected_goal.current_amount, selected_goal.target_amount)
                    st.markdown("**Progress**")
                    st.progress(progress / 100)
                    st.markdown(f"${selected_goal.current_amount:,.2f} of ${selected_goal.target_amount:,.2f}")
                
                with col3:
                    st.markdown("**Risk Level**")
                    st.markdown(f"**{selected_goal.risk_level}**")
                    
                    # Option to adjust risk
                    new_risk = st.selectbox(
                        "Adjust Risk",
                        options=["Low", "Medium", "High"],
                        index=["Low", "Medium", "High"].index(selected_goal.risk_level)
                    )
                    
                    if new_risk != selected_goal.risk_level and st.button("Update Risk"):
                        # Update the goal's risk level
                        if goal_utils.update_goal_risk_level(selected_goal.id, new_risk):
                            st.success(f"Risk level updated to {new_risk}")
                            st.rerun()  # Refresh to show the updated risk level
                        else:
                            st.error("Failed to update risk level")
                
                st.write("---")
                
                # Calculate remaining time and monthly investment
                now = datetime.datetime.utcnow()
                days_remaining = (selected_goal.target_date - now).days
                years_remaining = max(0, days_remaining / 365)
                expected_return = goal_utils.get_expected_return_rate(selected_goal.risk_level)
                
                monthly_investment = goal_utils.calculate_monthly_investment_needed(
                    selected_goal.target_amount, 
                    selected_goal.current_amount, 
                    years_remaining, 
                    expected_return
                )
                
                # Display monthly investment needed
                st.subheader("Investment Plan")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Monthly Investment Needed", 
                        value=f"${monthly_investment:,.2f}"
                    )
                    st.markdown(f"**Expected Return:** {expected_return*100:.1f}% annually")
                    st.markdown(f"**Time Remaining:** {days_remaining} days ({years_remaining:.1f} years)")
                
                # Get allocation recommendation based on goal parameters
                allocation = goal_utils.get_goal_based_allocation(selected_goal.risk_level, years_remaining)
                
                with col2:
                    # Display allocation chart
                    fig = px.pie(
                        names=list(allocation.keys()),
                        values=list(allocation.values()),
                        title="Recommended Portfolio Allocation",
                        color=list(allocation.keys()),
                        color_discrete_map=get_asset_category_color()
                    )
                    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed allocation strategy
                st.subheader("Investment Allocation Strategy")
                
                # Create columns for each asset category
                allocation_cols = st.columns(len(allocation))
                
                # For each category, show allocation percentage and a brief strategy
                for i, (category, percentage) in enumerate(allocation.items()):
                    with allocation_cols[i]:
                        st.metric(label=category, value=f"{percentage}%")
                        
                        # Display strategy based on category and risk
                        if category == "Large Cap":
                            st.markdown("Stable, established companies with market capitalization > $10 billion")
                        elif category == "Mid Cap":
                            st.markdown("Growing companies with market capitalization $2-10 billion")
                        elif category == "Small Cap":
                            st.markdown("Smaller companies with higher growth potential but higher risk")
                        elif category == "Gold":
                            st.markdown("Hedge against inflation and market volatility")
                        elif category == "ETFs/Crypto":
                            st.markdown("Diversified or specialized funds with targeted exposure")
                        elif category == "Bonds/Fixed Income":
                            st.markdown("Debt securities providing fixed interest payments and lower risk")
                
                # Investment amount calculator
                st.subheader("Calculate Your Investment Distribution")
                
                custom_amount = st.number_input(
                    "Monthly Investment Amount", 
                    min_value=0.0, 
                    value=monthly_investment, 
                    step=50.0
                )
                
                if custom_amount > 0:
                    st.markdown("#### Monthly Investment Distribution")
                    
                    # Calculate distribution amounts
                    distribution = {category: (percentage/100) * custom_amount for category, percentage in allocation.items()}
                    
                    # Create a DataFrame to display the distribution
                    dist_df = pd.DataFrame({
                        "Category": distribution.keys(),
                        "Allocation (%)": allocation.values(),
                        "Monthly Amount ($)": [f"${amount:.2f}" for amount in distribution.values()]
                    })
                    
                    st.dataframe(dist_df.set_index("Category"), use_container_width=True)
                    
                    # Option to save this as a portfolio
                    if st.button("Use This Allocation for My Portfolio"):
                        try:
                            # Create a new portfolio with this allocation
                            portfolio_id = db.create_goal_based_portfolio(
                                user_id=st.session_state[SESSION_KEYS.USER_ID],
                                goal_name=selected_goal.name,
                                allocation=allocation,
                                market=st.session_state[SESSION_KEYS.MARKET]
                            )
                            
                            if portfolio_id:
                                # Update session state to show the new portfolio
                                st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID] = portfolio_id
                                st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_NAME] = f"Goal Portfolio: {selected_goal.name}"
                                
                                # Create portfolio items
                                portfolio_items = []
                                for category, percentage in allocation.items():
                                    # Calculate suggested amount based on percentage
                                    # Using monthly investment * 12 as a starting point
                                    suggested_amount = (percentage / 100) * monthly_investment * 12
                                    
                                    # Add to portfolio
                                    portfolio_items.append({
                                        "name": f"{category} Allocation",
                                        "category": category,
                                        "amount": suggested_amount,
                                        "type": "Stock/ETF"
                                    })
                                
                                # Set in session state
                                st.session_state[SESSION_KEYS.PORTFOLIO] = portfolio_items
                                
                                # Save to database
                                save_current_portfolio_to_database()
                                
                                st.success(f"Portfolio created based on your {selected_goal.name} goal! Now you can select specific investments in each category.")
                                
                                # Provide option to go to portfolio management
                                if st.button("Go to Portfolio Management"):
                                    st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 4  # Portfolio management screen
                                    st.rerun()
                            else:
                                st.error("Failed to create portfolio")
                        except Exception as e:
                            st.error(f"Error creating portfolio: {e}")
                
                # Additional guidance
                st.subheader("Investment Strategy Guidance")
                
                if years_remaining < 5:
                    st.info("For short-term goals (less than 5 years), focus on capital preservation and liquidity. Consider more conservative investments like fixed income assets and high-quality bonds.")
                elif years_remaining < 15:
                    st.info("For medium-term goals (5-15 years), you can afford some market volatility. A balanced portfolio with both growth assets and income-generating investments is recommended.")
                else:
                    st.info("For long-term goals (15+ years), you can take advantage of market growth over time. Focus on growth-oriented investments with potentially higher returns, as you have time to recover from market downturns.")

def save_current_portfolio_to_database():
    """Save the current portfolio to the database"""
    if not st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
        st.warning("Please login to save your portfolio")
        return False
    
    if not st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID]:
        st.error("No current portfolio selected. Please create a new portfolio first.")
        return False
    
    portfolio_id = st.session_state[SESSION_KEYS.CURRENT_PORTFOLIO_ID]
    
    # First, delete existing investments for this portfolio
    # (This is a simple approach; in a production app you might want to update existing investments)
    investments = db.get_portfolio_investments(portfolio_id)
    for inv in investments:
        db.delete_investment(inv.id)
    
    # Now add all current investments
    for item in st.session_state[SESSION_KEYS.PORTFOLIO]:
        # Extract required fields
        name = item["name"]
        category = item["category"]
        amount = item["amount"]
        investment_type = item["type"]
        
        # Optional fields
        ticker = item.get("ticker")
        monthly_amount = item.get("monthly_amount")
        months_invested = item.get("months_invested")
        
        # Add to database
        db.add_investment(
            portfolio_id,
            name,
            category,
            amount,
            investment_type,
            ticker,
            monthly_amount,
            months_invested
        )
    
    # Save recommendation if available
    if st.session_state[SESSION_KEYS.ANALYSIS_RESULT] and st.session_state[SESSION_KEYS.RECOMMENDATIONS]:
        current_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["current_allocation"]
        target_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"]
        actions = st.session_state[SESSION_KEYS.RECOMMENDATIONS]["actions"]
        
        db.save_recommendation(portfolio_id, current_allocation, target_allocation, actions)
    
    # Update user risk profile if set
    if st.session_state[SESSION_KEYS.RISK_PROFILE]:
        db.update_user_risk_profile(st.session_state[SESSION_KEYS.USER_ID], st.session_state[SESSION_KEYS.RISK_PROFILE])
    
    return True

def show_price_alerts_screen():
    """
    Display the price alerts screen where users can create and manage stock price alerts
    """
    st.title("Price Alerts")
    
    # Check if user is logged in
    if not st.session_state[SESSION_KEYS.IS_LOGGED_IN]:
        st.warning("Please log in to use the price alerts feature.")
        if st.button("Go to Login"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 7  # Navigate to login screen
            st.rerun()
        return
    
    st.markdown("""
    ### Set up alerts for stock price movements
    
    Get notified when stocks reach your target price. You can set alerts for:
    - When a stock price rises above a certain value
    - When a stock price falls below a certain value
    
    Receive notifications via SMS when your alerts are triggered.
    """)
    
    # Tabs for creating and viewing alerts
    tab1, tab2 = st.tabs(["Create New Alert", "My Alerts"])
    
    with tab1:
        st.subheader("Create a New Price Alert")
        
        # Form for creating a new alert
        with st.form("create_alert_form"):
            # Stock ticker input
            ticker = st.text_input("Stock Ticker Symbol (e.g., AAPL, MSFT)")
            
            # Get current price if ticker is provided
            current_price = None
            if ticker:
                try:
                    price_data = fetch_stock_data([ticker])
                    if ticker in price_data:
                        current_price = price_data[ticker]['current_price']
                        st.info(f"Current price of {ticker}: ${current_price:.2f}")
                except Exception as e:
                    st.error(f"Error fetching price for {ticker}: {e}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Target price input
                target_price = st.number_input("Target Price ($)", min_value=0.01, step=0.1)
            
            with col2:
                # Alert type selection
                alert_type = st.radio(
                    "Alert me when price is:",
                    ["above", "below"],
                    horizontal=True
                )
            
            # Phone number for SMS alerts
            phone_number = st.text_input(
                "Phone Number for SMS Alerts (with country code, e.g., +1234567890)",
                placeholder="+1234567890"
            )
            
            # Submit button
            submitted = st.form_submit_button("Create Alert")
            
            # Process form submission
            if submitted:
                if not ticker:
                    st.error("Please enter a stock ticker symbol.")
                elif target_price <= 0:
                    st.error("Please enter a valid target price.")
                elif not phone_number or not phone_number.startswith("+"):
                    st.error("Please enter a valid phone number with country code starting with '+'.")
                else:
                    try:
                        # Create the alert
                        alert_id = create_price_alert(
                            st.session_state[SESSION_KEYS.USER_ID],
                            ticker.upper(),
                            target_price,
                            alert_type,
                            phone_number=phone_number
                        )
                        
                        if alert_id:
                            st.success(f"Price alert created for {ticker}! You'll be notified when the price is {alert_type} ${target_price:.2f}.")
                            st.rerun()
                        else:
                            st.error("Failed to create price alert. Please try again.")
                    except Exception as e:
                        st.error(f"Error creating alert: {e}")
    
    with tab2:
        st.subheader("Your Price Alerts")
        
        # Get user's alerts
        try:
            alerts = get_user_price_alerts(st.session_state[SESSION_KEYS.USER_ID])
            st.session_state[SESSION_KEYS.PRICE_ALERTS] = alerts
            
            if not alerts:
                st.info("You don't have any price alerts yet. Create one in the 'Create New Alert' tab.")
            else:
                # Fetch current prices for all tickers
                tickers = [alert.ticker for alert in alerts]
                current_prices = fetch_stock_data(tickers)
                
                # Display alerts in a table
                for alert in alerts:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
                        with col1:
                            st.write(f"**{alert.ticker}**")
                            if alert.is_triggered:
                                st.write("✅ Triggered")
                            elif not alert.is_active:
                                st.write("❌ Inactive")
                            else:
                                st.write("🔔 Active")
                        
                        with col2:
                            # Alert details
                            direction = "above" if alert.alert_type == "above" else "below"
                            st.write(f"Alert when price goes {direction} ${alert.target_price:.2f}")
                            
                            # Show phone number if available
                            if alert.phone_number:
                                st.write(f"SMS to: {alert.phone_number}")
                        
                        with col3:
                            # Current price
                            if alert.ticker in current_prices:
                                price = current_prices[alert.ticker]['current_price']
                                st.write(f"Current price: ${price:.2f}")
                                
                                # Price difference
                                diff = price - alert.target_price
                                diff_percent = (diff / alert.target_price) * 100
                                
                                if alert.alert_type == 'above':
                                    needed_change = alert.target_price - price if price < alert.target_price else 0
                                    if needed_change > 0:
                                        st.write(f"Needs to rise: ${needed_change:.2f} ({abs(diff_percent):.1f}%)")
                                    else:
                                        st.write(f"Above target: ${abs(diff):.2f} ({abs(diff_percent):.1f}%)")
                                else:
                                    needed_change = price - alert.target_price if price > alert.target_price else 0
                                    if needed_change > 0:
                                        st.write(f"Needs to fall: ${needed_change:.2f} ({abs(diff_percent):.1f}%)")
                                    else:
                                        st.write(f"Below target: ${abs(diff):.2f} ({abs(diff_percent):.1f}%)")
                            else:
                                st.write("Unable to fetch current price")
                        
                        with col4:
                            # Delete button
                            if not alert.is_triggered and alert.is_active:
                                if st.button("Delete", key=f"delete_{alert.id}"):
                                    if delete_price_alert(alert.id):
                                        st.success(f"Alert for {alert.ticker} deleted")
                                        st.rerun()
                    
                    st.divider()
                
                # Check alerts button
                if st.button("Check Alerts Now"):
                    with st.spinner("Checking your price alerts..."):
                        # Check if any alerts are triggered
                        triggered_alerts = check_price_alerts(current_prices)
                        
                        if triggered_alerts:
                            # Try to send SMS notifications
                            sent_alerts = send_sms_price_alerts(triggered_alerts)
                            
                            if sent_alerts:
                                st.success(f"{len(sent_alerts)} alert(s) triggered and SMS notifications sent!")
                            else:
                                st.warning(f"{len(triggered_alerts)} alert(s) triggered but SMS notifications could not be sent. Please check your Twilio settings.")
                        else:
                            st.info("No alerts triggered at this time.")
                        
                        # Refresh the page to show updated alert statuses
                        st.rerun()
        
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
    
    # Navigation options
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Back to Portfolio Management", use_container_width=True):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 7
            st.rerun()
    
    with col2:
        if st.button("View Financial Goals", use_container_width=True):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 8
            st.rerun()
    
    # Check if Twilio credentials are set
    twilio_ready = all([
        os.environ.get("TWILIO_ACCOUNT_SID"),
        os.environ.get("TWILIO_AUTH_TOKEN"),
        os.environ.get("TWILIO_PHONE_NUMBER")
    ])
    
    if not twilio_ready:
        st.warning("""
        **Twilio credentials not found**: To enable SMS notifications, please set the following environment variables:
        - TWILIO_ACCOUNT_SID
        - TWILIO_AUTH_TOKEN
        - TWILIO_PHONE_NUMBER
        
        Alerts will still be tracked, but SMS notifications will not be sent until these credentials are provided.
        """)

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import SESSION_KEYS, initialize_session_state, get_risk_profile_allocation, get_asset_category_color
from portfolio_analyzer import analyze_portfolio, get_allocation_recommendation
from stock_service import get_stock_suggestions, fetch_stock_data, get_sip_suggestions

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
        
        # Only show navigation options once risk is selected
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Portfolio", use_container_width=True):
            st.session_state[SESSION_KEYS.PORTFOLIO] = []
            st.rerun()
    
    with col2:
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

if __name__ == "__main__":
    main()
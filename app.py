import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from portfolio_analyzer import analyze_portfolio, get_allocation_recommendation
from stock_service import get_stock_suggestions, fetch_stock_data
from utils import SESSION_KEYS, initialize_session_state, get_risk_profile_allocation, get_asset_category_color

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
    - Personalized stock suggestions
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
    
    Add your existing stocks and investments to analyze your portfolio.
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
    
    # Form for adding new stock
    with st.form("add_stock_form"):
        st.subheader("Add Investment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stock_name = st.text_input("Stock/Investment Name")
        
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
                "amount": investment_amount
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
    st.subheader("Select a category to view stock recommendations")
    
    categories = list(st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"].keys())
    selected_category = st.selectbox("Category", categories)
    
    if selected_category:
        st.session_state[SESSION_KEYS.SELECTED_CATEGORY] = selected_category
    
    if st.button("View Stock Recommendations", use_container_width=True):
        st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 5
        st.rerun()

def show_stock_selection_screen():
    st.title("Stock Selection")
    
    if not st.session_state.get(SESSION_KEYS.SELECTED_CATEGORY):
        st.warning("No category selected. Please go back and select a category.")
        if st.button("Back to Recommendations"):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 4
            st.rerun()
        return
    
    selected_category = st.session_state[SESSION_KEYS.SELECTED_CATEGORY]
    
    st.subheader(f"Recommended {selected_category} Stocks")
    
    # Get stock suggestions for the selected category
    suggested_stocks = get_stock_suggestions(selected_category)
    
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
            
            st.divider()
    else:
        st.info(f"No stock suggestions available for {selected_category}. Try another category.")
    
    # Show allocation for this category
    total_portfolio = sum(item['amount'] for item in st.session_state[SESSION_KEYS.PORTFOLIO])
    target_percentage = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"].get(selected_category, 0)
    target_amount = total_portfolio * (target_percentage / 100)
    
    st.subheader("Budget Allocation")
    st.info(f"Based on your risk profile, you should allocate ${target_amount:,.2f} ({target_percentage}%) to {selected_category}")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Back to Categories", use_container_width=True):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 4
            st.rerun()
    
    with col2:
        if st.button("View Summary", use_container_width=True):
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 6
            st.rerun()

def show_summary_screen():
    st.title("Investment Summary")
    
    # Display the risk profile
    st.subheader("Your Risk Profile")
    st.info(st.session_state[SESSION_KEYS.RISK_PROFILE])
    
    # Display current portfolio summary
    if st.session_state[SESSION_KEYS.PORTFOLIO]:
        st.subheader("Current Portfolio")
        
        current_data = {}
        for item in st.session_state[SESSION_KEYS.PORTFOLIO]:
            category = item['category']
            if category not in current_data:
                current_data[category] = 0
            current_data[category] += item['amount']
        
        total_portfolio = sum(current_data.values())
        
        df = pd.DataFrame({
            'Category': list(current_data.keys()),
            'Amount ($)': list(current_data.values()),
            'Percentage (%)': [amount/total_portfolio*100 for amount in current_data.values()]
        })
        
        st.dataframe(df, use_container_width=True)
    
    # Display recommended allocation
    if st.session_state[SESSION_KEYS.ANALYSIS_RESULT]:
        st.subheader("Recommended Allocation")
        
        target_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"]
        
        df = pd.DataFrame({
            'Category': list(target_allocation.keys()),
            'Percentage (%)': list(target_allocation.values()),
            'Amount ($)': [total_portfolio * (pct/100) for pct in target_allocation.values()]
        })
        
        st.dataframe(df, use_container_width=True)
    
    # Display selected stocks
    if st.session_state.get(SESSION_KEYS.SELECTED_STOCKS):
        st.subheader("Selected Investments")
        
        all_selected = []
        
        for category, stocks in st.session_state[SESSION_KEYS.SELECTED_STOCKS].items():
            if stocks:
                target_percentage = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"].get(category, 0)
                target_amount = total_portfolio * (target_percentage / 100)
                
                # Calculate per-stock allocation
                if len(stocks) > 0:
                    per_stock_amount = target_amount / len(stocks)
                    
                    for stock in stocks:
                        all_selected.append({
                            'Category': category,
                            'Ticker': stock['ticker'],
                            'Name': stock['name'],
                            'Current Price': f"${stock['price']:.2f}",
                            'Recommended Investment': f"${per_stock_amount:.2f}"
                        })
        
        if all_selected:
            st.dataframe(pd.DataFrame(all_selected), use_container_width=True)
        else:
            st.info("No stocks selected yet. Please go back to the Stock Selection screen to choose stocks.")
    
    # Visual summary
    st.subheader("Portfolio Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Current allocation chart
        current_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["current_allocation"]
        
        fig = px.pie(
            names=list(current_allocation.keys()),
            values=list(current_allocation.values()),
            title="Current Distribution",
            color=list(current_allocation.keys()),
            color_discrete_map=get_asset_category_color()
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Target allocation chart
        target_allocation = st.session_state[SESSION_KEYS.ANALYSIS_RESULT]["target_allocation"]
        
        fig = px.pie(
            names=list(target_allocation.keys()),
            values=list(target_allocation.values()),
            title="Recommended Distribution",
            color=list(target_allocation.keys()),
            color_discrete_map=get_asset_category_color()
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Next steps
    st.subheader("Next Steps")
    
    st.markdown("""
    ### To implement your investment plan:
    
    1. **Review your selected investments** and make any necessary adjustments.
    2. **Contact your broker** or use your preferred investment platform to make the recommended trades.
    3. **Set a reminder** to rebalance your portfolio periodically (quarterly is recommended).
    4. **Track your investments** and adjust as needed based on market conditions and your changing financial goals.
    """)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Over", use_container_width=True):
            # Reset session state
            for key in SESSION_KEYS:
                if key != "NAVIGATION_INDEX":
                    if key in st.session_state:
                        del st.session_state[key]
            
            st.session_state[SESSION_KEYS.NAVIGATION_INDEX] = 0
            st.rerun()
    
    with col2:
        if st.button("Save Plan (PDF)", use_container_width=True):
            st.info("This functionality will be implemented in a future version.")

if __name__ == "__main__":
    main()

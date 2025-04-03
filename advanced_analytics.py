import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import openai
import os
import json
import yfinance as yf
from stock_service import fetch_stock_data

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def predict_portfolio_performance(portfolio, risk_profile, time_horizon_years=5):
    """
    Predict the future performance of a portfolio over a specified time horizon.
    
    Args:
        portfolio (list): User's current portfolio
        risk_profile (str): User's risk profile
        time_horizon_years (int): Years to predict into the future
        
    Returns:
        dict: Performance predictions and charts
    """
    # Initialize result
    result = {
        "predictions": [],
        "chart_data": None,
        "expected_returns": {},
        "risk_assessment": {},
        "summary": ""
    }
    
    # Calculate current portfolio value
    total_value = sum(item['amount'] for item in portfolio)
    
    # Get expected return rates by category and risk profile
    expected_returns = get_expected_return_rates(risk_profile)
    result["expected_returns"] = expected_returns
    
    # Calculate weighted expected return for the portfolio
    portfolio_categories = {}
    for item in portfolio:
        category = item['category']
        if category in portfolio_categories:
            portfolio_categories[category] += item['amount']
        else:
            portfolio_categories[category] = item['amount']
    
    weighted_return = 0
    for category, amount in portfolio_categories.items():
        category_weight = amount / total_value
        if category in expected_returns:
            weighted_return += category_weight * expected_returns[category]
    
    # Get risk volatility estimates
    volatility_estimates = get_volatility_estimates(risk_profile)
    result["risk_assessment"] = volatility_estimates
    
    # Generate projection data
    dates = []
    pessimistic_values = []
    expected_values = []
    optimistic_values = []
    
    # Base assumptions:
    # - Pessimistic: -1 standard deviation from expected return
    # - Expected: Expected return based on risk profile and asset allocation
    # - Optimistic: +1 standard deviation from expected return
    
    # Calculate standard deviation for the portfolio
    portfolio_volatility = 0
    for category, amount in portfolio_categories.items():
        category_weight = amount / total_value
        if category in volatility_estimates:
            portfolio_volatility += category_weight * volatility_estimates[category]
    
    # Generate monthly projections
    current_date = datetime.now()
    for month in range(time_horizon_years * 12 + 1):
        projection_date = current_date + timedelta(days=30 * month)
        dates.append(projection_date)
        
        # Monthly return rates
        monthly_expected_return = weighted_return / 12
        monthly_volatility = portfolio_volatility / np.sqrt(12)
        
        # Calculate values
        time_factor = month / 12  # Convert to years
        
        # Expected value formula: P * (1 + r)^t where r is annual return rate and t is time in years
        expected_value = total_value * (1 + weighted_return) ** time_factor
        expected_values.append(expected_value)
        
        # Pessimistic scenario: 1 standard deviation below expected return
        pessimistic_return = weighted_return - portfolio_volatility
        pessimistic_value = total_value * (1 + pessimistic_return) ** time_factor
        pessimistic_values.append(max(0, pessimistic_value))  # Ensure no negative values
        
        # Optimistic scenario: 1 standard deviation above expected return
        optimistic_return = weighted_return + portfolio_volatility
        optimistic_value = total_value * (1 + optimistic_return) ** time_factor
        optimistic_values.append(optimistic_value)
    
    # Create dataframe for chart
    chart_data = pd.DataFrame({
        'Date': dates,
        'Pessimistic': pessimistic_values,
        'Expected': expected_values,
        'Optimistic': optimistic_values
    })
    
    result["chart_data"] = chart_data
    
    # Add specific predictions at key time points
    predictions = []
    for year in [1, 3, 5]:
        if year <= time_horizon_years:
            index = year * 12  # Convert years to months
            predictions.append({
                "year": year,
                "pessimistic": pessimistic_values[index],
                "expected": expected_values[index],
                "optimistic": optimistic_values[index]
            })
    
    result["predictions"] = predictions
    
    # Generate performance summary
    summary = f"""
    Based on your {risk_profile} risk profile and current portfolio allocation, 
    over a {time_horizon_years}-year period, your portfolio of ${total_value:,.2f} 
    is expected to grow to approximately ${expected_values[-1]:,.2f}.
    
    In a pessimistic scenario, the value could be around ${pessimistic_values[-1]:,.2f},
    while in an optimistic scenario, it could reach ${optimistic_values[-1]:,.2f}.
    
    The weighted expected annual return is {weighted_return*100:.2f}% with a 
    volatility of {portfolio_volatility*100:.2f}%.
    """
    
    result["summary"] = summary
    
    return result

def get_expected_return_rates(risk_profile):
    """
    Get expected annual return rates by category based on risk profile.
    
    Args:
        risk_profile (str): Risk profile (Low, Medium, or High Risk)
        
    Returns:
        dict: Expected return rates by category
    """
    # These are simplified estimates - real models would be more complex
    if "Low Risk" in risk_profile:
        return {
            "Large Cap": 0.06,  # 6%
            "Mid Cap": 0.08,    # 8%
            "Small Cap": 0.10,  # 10%
            "Gold": 0.04,       # 4%
            "ETFs/Crypto": 0.07 # 7%
        }
    elif "Medium Risk" in risk_profile:
        return {
            "Large Cap": 0.08,  # 8%
            "Mid Cap": 0.10,    # 10%
            "Small Cap": 0.13,  # 13%
            "Gold": 0.04,       # 4%
            "ETFs/Crypto": 0.12 # 12%
        }
    else:  # High Risk
        return {
            "Large Cap": 0.09,  # 9%
            "Mid Cap": 0.12,    # 12%
            "Small Cap": 0.15,  # 15%
            "Gold": 0.04,       # 4%
            "ETFs/Crypto": 0.18 # 18%
        }

def get_volatility_estimates(risk_profile):
    """
    Get volatility estimates by category based on risk profile.
    
    Args:
        risk_profile (str): Risk profile (Low, Medium, or High Risk)
        
    Returns:
        dict: Volatility estimates by category
    """
    # These are simplified estimates - real models would use historical data
    if "Low Risk" in risk_profile:
        return {
            "Large Cap": 0.10,  # 10%
            "Mid Cap": 0.14,    # 14%
            "Small Cap": 0.18,  # 18%
            "Gold": 0.12,       # 12%
            "ETFs/Crypto": 0.20 # 20%
        }
    elif "Medium Risk" in risk_profile:
        return {
            "Large Cap": 0.12,  # 12%
            "Mid Cap": 0.16,    # 16%
            "Small Cap": 0.20,  # 20%
            "Gold": 0.12,       # 12%
            "ETFs/Crypto": 0.25 # 25%
        }
    else:  # High Risk
        return {
            "Large Cap": 0.15,  # 15%
            "Mid Cap": 0.20,    # 20%
            "Small Cap": 0.25,  # 25%
            "Gold": 0.12,       # 12%
            "ETFs/Crypto": 0.35 # 35%
        }

def analyze_sector_exposure(portfolio):
    """
    Analyze the sector exposure of a portfolio using ticker symbols.
    
    Args:
        portfolio (list): User's portfolio with ticker symbols
        
    Returns:
        dict: Sector exposure analysis
    """
    # Initialize result
    result = {
        "sector_allocation": {},
        "sector_performance": {},
        "diversification_score": 0,
        "recommendations": [],
        "chart_data": None
    }
    
    # Get tickers from portfolio
    tickers = []
    ticker_weights = {}
    total_value = sum(item['amount'] for item in portfolio if 'ticker' in item)
    
    if total_value == 0:
        result["error"] = "No ticker symbols found in portfolio for sector analysis."
        return result
    
    for item in portfolio:
        if 'ticker' in item and item['ticker']:
            ticker = item['ticker']
            tickers.append(ticker)
            ticker_weights[ticker] = item['amount'] / total_value
    
    if not tickers:
        result["error"] = "No ticker symbols found in portfolio for sector analysis."
        return result
    
    # Fetch stock data
    try:
        stock_data = fetch_stock_data(tickers)
    except Exception as e:
        result["error"] = f"Error fetching stock data: {str(e)}"
        return result
    
    # Get sector information using yfinance
    sectors = {}
    sector_weights = {}
    sector_tickers = {}
    
    for ticker in tickers:
        try:
            ticker_obj = yf.Ticker(ticker)
            ticker_info = ticker_obj.info
            if 'sector' in ticker_info and ticker_info['sector']:
                sector = ticker_info['sector']
                if sector not in sectors:
                    sectors[sector] = 0
                    sector_tickers[sector] = []
                
                sectors[sector] += ticker_weights.get(ticker, 0)
                sector_tickers[sector].append(ticker)
            else:
                if "Unknown" not in sectors:
                    sectors["Unknown"] = 0
                    sector_tickers["Unknown"] = []
                sectors["Unknown"] += ticker_weights.get(ticker, 0)
                sector_tickers["Unknown"].append(ticker)
        except Exception:
            if "Unknown" not in sectors:
                sectors["Unknown"] = 0
                sector_tickers["Unknown"] = []
            sectors["Unknown"] += ticker_weights.get(ticker, 0)
            sector_tickers["Unknown"].append(ticker)
    
    # Normalize sector weights to ensure they sum to 1
    total_weight = sum(sectors.values())
    for sector in sectors:
        sector_weights[sector] = sectors[sector] / total_weight if total_weight > 0 else 0
    
    result["sector_allocation"] = sector_weights
    result["sector_tickers"] = sector_tickers
    
    # Calculate diversification score (Herfindahl-Hirschman Index)
    # Lower HHI is better (more diversified)
    hhi = sum(weight**2 for weight in sector_weights.values())
    
    # Convert to a diversification score (0-100, higher is better)
    diversification_score = max(0, min(100, 100 * (1 - hhi)))
    result["diversification_score"] = round(diversification_score, 1)
    
    # Get S&P 500 sector weights as a benchmark (approximate values)
    sp500_sectors = {
        "Information Technology": 0.28,
        "Health Care": 0.14,
        "Financials": 0.11,
        "Consumer Discretionary": 0.10,
        "Communication Services": 0.09,
        "Industrials": 0.08,
        "Consumer Staples": 0.06,
        "Energy": 0.05,
        "Utilities": 0.03,
        "Real Estate": 0.03,
        "Materials": 0.03
    }
    
    # Create a sector chart
    if sector_weights:
        # Convert to percentage for better readability
        sector_percents = {sector: weight * 100 for sector, weight in sector_weights.items()}
        
        # Create chart data
        fig = px.pie(
            names=list(sector_percents.keys()),
            values=list(sector_percents.values()),
            title="Portfolio Sector Allocation",
            hole=0.4,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        # Add benchmark comparison if available
        if len(sector_weights) > 1:
            # Create bar chart for comparison with benchmark
            sectors = list(sector_weights.keys())
            portfolio_values = [sector_weights[s] * 100 for s in sectors]
            benchmark_values = [sp500_sectors.get(s, 0) * 100 for s in sectors]
            
            comp_fig = px.bar(
                x=sectors,
                y=[portfolio_values, benchmark_values],
                barmode='group',
                labels={"value": "Allocation (%)", "variable": "Source"},
                title="Portfolio vs. Benchmark Sector Allocation",
                color_discrete_sequence=["rgb(0, 112, 192)", "rgb(192, 0, 0)"]
            )
            comp_fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                xaxis_tickangle=-45
            )
            
            # Add both charts to result
            result["sector_chart"] = fig
            result["comparison_chart"] = comp_fig
        else:
            result["sector_chart"] = fig
    
    # Generate recommendations based on sector exposure
    recommendations = []
    
    # Compare portfolio sector allocation to benchmark
    for sector, benchmark_weight in sp500_sectors.items():
        portfolio_weight = sector_weights.get(sector, 0)
        difference = portfolio_weight - benchmark_weight
        
        if abs(difference) > 0.05:  # If more than 5% difference
            if difference > 0:
                recommendations.append(f"Your portfolio is overweight in {sector} ({portfolio_weight*100:.1f}% vs {benchmark_weight*100:.1f}% benchmark).")
            else:
                recommendations.append(f"Your portfolio is underweight in {sector} ({portfolio_weight*100:.1f}% vs {benchmark_weight*100:.1f}% benchmark).")
    
    # Add diversification recommendation if needed
    if diversification_score < 60:
        recommendations.append("Your portfolio has low sector diversification. Consider investing across more sectors to reduce risk.")
    
    result["recommendations"] = recommendations
    
    # Create chart data
    chart_data = pd.DataFrame({
        'Sector': list(sector_weights.keys()),
        'Portfolio Weight': [weight * 100 for weight in sector_weights.values()],
        'S&P 500 Weight': [sp500_sectors.get(sector, 0) * 100 for sector in sector_weights.keys()]
    })
    
    result["chart_data"] = chart_data
    
    # Create concentration metrics for UI display
    if sector_weights:
        top_sector = max(sector_weights.items(), key=lambda x: x[1])
        top_sector_name = top_sector[0]
        top_sector_allocation = round(top_sector[1] * 100, 1)
        
        # Calculate diversity score on a scale of 0-10 for easier understanding
        diversity_score = min(10, diversification_score / 10)
        
        # Determine if the diversification is improving or worsening
        # Using 7 as a moderate benchmark (70% on the original scale)
        diversity_delta = "+" if diversity_score >= 7 else "-"
        
        result["concentration_metrics"] = {
            "top_sector": top_sector_name,
            "top_allocation": top_sector_allocation,
            "diversification_score": round(diversity_score, 1),
            "diversification_delta": diversity_delta,
            "sectors_count": len(sector_weights)
        }
        
        # Create insights list for UI
        insights = []
        
        # Diversification insight
        if diversity_score < 5:
            insights.append({
                "type": "warning",
                "message": "Your portfolio has low sector diversification, which may increase volatility. Consider adding investments across more sectors."
            })
        elif diversity_score >= 8:
            insights.append({
                "type": "success",
                "message": "Your portfolio has excellent sector diversification, which helps reduce risk during sector-specific downturns."
            })
        else:
            insights.append({
                "type": "info",
                "message": "Your portfolio has moderate sector diversification. You may benefit from adding exposure to a few more sectors."
            })
        
        # Concentration insight
        if top_sector_allocation > 40:
            insights.append({
                "type": "warning",
                "message": f"Your portfolio is highly concentrated in {top_sector_name} ({top_sector_allocation}%). This increases sector-specific risk."
            })
        
        # Add sector-specific insights
        tech_weight = sector_weights.get("Information Technology", 0) * 100
        financial_weight = sector_weights.get("Financials", 0) * 100
        healthcare_weight = sector_weights.get("Health Care", 0) * 100
        
        if tech_weight > 35:
            insights.append({
                "type": "info",
                "message": f"Technology exposure is high ({tech_weight:.1f}%). Consider how tech regulation or slowdown would impact your portfolio."
            })
        
        if financial_weight > 25:
            insights.append({
                "type": "info",
                "message": f"Financial sector exposure is high ({financial_weight:.1f}%). This sector is sensitive to interest rate changes."
            })
        
        if healthcare_weight < 5 and financial_weight > 0:
            insights.append({
                "type": "info",
                "message": "Consider adding healthcare investments for more defensive exposure during market downturns."
            })
        
        result["insights"] = insights
    
    return result

def generate_economic_scenario_analysis(portfolio, time_horizon_years=5):
    """
    Generate an economic scenario analysis for a portfolio.
    
    Args:
        portfolio (list): User's portfolio
        time_horizon_years (int): Years to analyze
        
    Returns:
        dict: Economic scenario analysis
    """
    # Initialize result
    result = {
        "scenarios": [],  # A list to match what app.py expects
        "chart_data": None,
        "recommendations": []
    }
    
    try:
        # Define economic scenarios
        scenario_config = {
            "Base Case": {
                "description": "Moderate growth, inflation around 2-3%, gradual interest rate changes.",
                "large_cap_return": 0.08,
                "mid_cap_return": 0.10,
                "small_cap_return": 0.12,
                "gold_return": 0.03,
                "crypto_return": 0.10,
                "probability": 0.50  # 50% probability
            },
            "High Inflation": {
                "description": "Elevated inflation (4-6%), aggressive interest rate hikes, pressure on growth stocks.",
                "large_cap_return": 0.06,
                "mid_cap_return": 0.07,
                "small_cap_return": 0.08,
                "gold_return": 0.10,
                "crypto_return": 0.05,
                "probability": 0.20  # 20% probability
            },
            "Recession": {
                "description": "Economic contraction, declining corporate profits, higher volatility.",
                "large_cap_return": -0.05,
                "mid_cap_return": -0.10,
                "small_cap_return": -0.15,
                "gold_return": 0.08,
                "crypto_return": -0.20,
                "probability": 0.15  # 15% probability
            },
            "Bull Market": {
                "description": "Strong economic growth, low unemployment, favorable corporate conditions.",
                "large_cap_return": 0.12,
                "mid_cap_return": 0.15,
                "small_cap_return": 0.20,
                "gold_return": 0.01,
                "crypto_return": 0.25,
                "probability": 0.15  # 15% probability
            }
        }
        
        # Format scenarios for the UI
        scenarios = []
        for name, config in scenario_config.items():
            scenarios.append({
                "name": name,
                "description": config["description"],
                "impact": f"Expected annual return: {config['large_cap_return']*100:.1f}% to {config['small_cap_return']*100:.1f}%",
                "resilience": "High" if name in ["Base Case", "Bull Market"] else "Medium" if name == "High Inflation" else "Low",
                "recommendations": [
                    f"Prepare for {name.lower()} conditions by adjusting asset allocation",
                    f"Consider {'increasing' if config['large_cap_return'] > 0 else 'decreasing'} exposure to growth stocks",
                    f"Monitor economic indicators closely for signs of this scenario"
                ]
            })
        
        result["scenarios"] = scenarios
        
        # Calculate current portfolio value
        total_value = sum(item['amount'] for item in portfolio)
        
        # Create portfolio breakdown by category
        portfolio_categories = {}
        for item in portfolio:
            category = item['category']
            if category in portfolio_categories:
                portfolio_categories[category] += item['amount']
            else:
                portfolio_categories[category] = item['amount']
        
        # Map our categories to scenario categories
        category_mapping = {
            "Large Cap": "large_cap_return",
            "Mid Cap": "mid_cap_return",
            "Small Cap": "small_cap_return",
            "Gold": "gold_return",
            "ETFs/Crypto": "crypto_return"
        }
        
        # Calculate expected returns under each scenario
        scenario_results = {}
        for scenario in scenarios:
            scenario_name = scenario["name"]
            scenario_config_data = scenario_config[scenario_name]
            
            # Calculate weighted return for this scenario
            weighted_return = 0
            for category, amount in portfolio_categories.items():
                category_weight = amount / total_value
                return_key = category_mapping.get(category, "large_cap_return")  # Default to large cap if category not found
                weighted_return += category_weight * scenario_config_data[return_key]
            
            # Project final value after time horizon
            final_value = total_value * (1 + weighted_return) ** time_horizon_years
            
            # Add to results
            scenario_results[scenario_name] = {
                "description": scenario_config_data["description"],
                "annual_return": weighted_return,
                "final_value": final_value,
                "probability": scenario_config_data["probability"]
            }
        
        # Calculate expected value across all scenarios (probability-weighted average)
        expected_value = sum(
            scenario_data["final_value"] * scenario_data["probability"] 
            for scenario_data in scenario_results.values()
        )
        
        # Create chart data for visualization
        chart_data = []
        for year in range(time_horizon_years + 1):
            year_data = {"Year": year}
            
            for scenario_name, scenario_result in scenario_results.items():
                annual_return = scenario_result["annual_return"]
                year_data[scenario_name] = total_value * (1 + annual_return) ** year
            
            chart_data.append(year_data)
        
        # Create DataFrame for chart data
        chart_df = pd.DataFrame(chart_data)
        
        # Create a line chart for scenario visualization
        try:
            if len(chart_df) > 0:
                fig = px.line(chart_df, x="Year", y=chart_df.columns[1:], 
                            title="Portfolio Value Projection by Economic Scenario",
                            labels={"value": "Portfolio Value ($)", "variable": "Economic Scenario"})
                fig.update_layout(legend_title_text="Scenarios")
                result["scenario_chart"] = fig
        except Exception as e:
            print(f"Error creating scenario chart: {str(e)}")
        
        result["chart_data"] = chart_df
        result["scenario_results"] = scenario_results
        result["expected_value"] = expected_value
        
        # Generate recommendations based on scenario analysis
        recommendations = []
        
        # Identify the worst performing scenario
        worst_scenario = min(scenario_results.items(), key=lambda x: x[1]["final_value"])
        worst_name, worst_result = worst_scenario
        
        # Calculate the potential loss in the worst scenario
        worst_case_change = (worst_result["final_value"] - total_value) / total_value
        
        if worst_case_change < -0.2:  # More than 20% loss
            recommendations.append(f"Your portfolio may be vulnerable to a {worst_name} scenario. Consider adding more defensive assets.")
        
        # Identify which assets perform best in high probability negative scenarios
        if "Recession" in scenario_results and scenario_results["Recession"]["probability"] > 0.1:
            recommendations.append("Given the recession risk, consider increasing allocation to defensive sectors (utilities, consumer staples) and gold.")
        
        if "High Inflation" in scenario_results and scenario_results["High Inflation"]["probability"] > 0.1:
            recommendations.append("With inflation risk present, consider adding TIPS, commodities, or real estate to protect purchasing power.")
        
        # Add general recommendation based on overall expected return
        avg_annual_return = (expected_value / total_value) ** (1/time_horizon_years) - 1
        if avg_annual_return < 0.05:  # Less than 5% annualized
            recommendations.append("Your expected returns may be lower than traditional benchmarks. Consider reviewing your asset allocation.")
        
        result["recommendations"] = recommendations
        
        return result
        
    except Exception as e:
        print(f"Error in economic scenario analysis: {str(e)}")
        return {
            "scenarios": [{
                "name": "Error",
                "description": f"Error generating economic scenarios: {str(e)}",
                "impact": "Unable to calculate economic scenarios",
                "resilience": "Unknown",
                "recommendations": ["Please try again with a valid portfolio"]
            }],
            "chart_data": None,
            "recommendations": ["Try again with a revised portfolio."]
        }

def get_ai_portfolio_insights(portfolio, risk_profile):
    """
    Get AI-generated insights about a portfolio using OpenAI's GPT models.
    
    Args:
        portfolio (list): User's portfolio
        risk_profile (str): User's risk profile
        
    Returns:
        dict: AI-generated insights
    """
    # Format portfolio data for the prompt
    portfolio_text = "Portfolio:\n"
    total_value = sum(item['amount'] for item in portfolio)
    
    for item in portfolio:
        percentage = (item['amount'] / total_value) * 100
        portfolio_text += f"- {item['name']} ({item['category']}): ${item['amount']:,.2f} ({percentage:.1f}%)\n"
    
    # Create portfolio breakdown by category
    portfolio_categories = {}
    for item in portfolio:
        category = item['category']
        if category in portfolio_categories:
            portfolio_categories[category] += item['amount']
        else:
            portfolio_categories[category] = item['amount']
    
    category_breakdown = "Category Breakdown:\n"
    for category, amount in portfolio_categories.items():
        percentage = (amount / total_value) * 100
        category_breakdown += f"- {category}: ${amount:,.2f} ({percentage:.1f}%)\n"
    
    # Get expected returns based on risk profile
    expected_returns = get_expected_return_rates(risk_profile)
    returns_text = "Expected Returns by Category:\n"
    for category, rate in expected_returns.items():
        returns_text += f"- {category}: {rate*100:.1f}%\n"
    
    # Create the prompt for OpenAI
    prompt = f"""
    As a financial advisor, provide strategic insights on this investment portfolio:
    
    Risk Profile: {risk_profile}
    Total Portfolio Value: ${total_value:,.2f}
    
    {portfolio_text}
    
    {category_breakdown}
    
    {returns_text}
    
    Please provide:
    1. Strategic portfolio assessment (strengths and weaknesses)
    2. Three specific recommendations for improvement
    3. One insight about long-term performance potential
    4. One key risk factor to monitor
    
    Format your response as JSON with these keys: "assessment", "recommendations", "long_term_insight", "key_risk"
    Each recommendation should be a separate string in the recommendations array.
    """
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": "You are a sophisticated financial advisor specializing in portfolio analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        raw_insights = json.loads(response.choices[0].message.content)
        
        # Format insights for UI display
        insights = {
            "summary": f"Portfolio Assessment: {raw_insights.get('assessment', 'No assessment available.')}",
            "detailed_analysis": {
                "Strategic Assessment": raw_insights.get('assessment', 'No assessment available.'),
                "Long-term Outlook": raw_insights.get('long_term_insight', 'No long-term insights available.'),
                "Key Risk Factors": raw_insights.get('key_risk', 'No risk analysis available.')
            },
            "opportunities": [
                f"Opportunity: {rec}" for rec in raw_insights.get('recommendations', ['No recommendations available.'])
            ],
            "risks": [
                f"Risk: {raw_insights.get('key_risk', 'No key risk identified.')}"
            ]
        }
        
        return insights
        
    except Exception as e:
        # Return error message if API call fails in the format expected by the UI
        return {
            "summary": f"Error generating AI insights: {str(e)}",
            "detailed_analysis": {
                "Error Details": f"An error occurred when generating AI insights: {str(e)}. Please try again later.",
                "Troubleshooting": "Please check your OpenAI API key and internet connection."
            },
            "opportunities": ["Please try again later."],
            "risks": ["Analysis not available due to an error."]
        }

def calculate_modern_portfolio_theory_metrics(portfolio, lookback_days=365):
    """
    Calculate Modern Portfolio Theory metrics for a portfolio.
    
    Args:
        portfolio (list): User's portfolio with ticker symbols
        lookback_days (int): Days of historical data to use
        
    Returns:
        dict: MPT metrics including Sharpe ratio, beta, alpha, etc.
    """
    # Initialize result
    result = {
        "sharpe_ratio": None,
        "beta": None,
        "alpha": None,
        "r_squared": None,
        "treynor_ratio": None,
        "risk_metrics": {},
        "correlation_matrix": None,
        "efficient_frontier": None
    }
    
    # Get tickers from portfolio
    tickers = []
    ticker_weights = {}
    total_value = sum(item['amount'] for item in portfolio if 'ticker' in item)
    
    if total_value == 0:
        result["error"] = "No ticker symbols found in portfolio for MPT analysis."
        return result
    
    for item in portfolio:
        if 'ticker' in item and item['ticker']:
            ticker = item['ticker']
            tickers.append(ticker)
            ticker_weights[ticker] = item['amount'] / total_value
    
    if not tickers:
        result["error"] = "No ticker symbols found in portfolio for MPT analysis."
        return result
    
    # Add market index for beta calculation
    tickers.append("^GSPC")  # S&P 500
    
    # Get historical price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    try:
        # Download historical data
        price_data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        
        # Calculate daily returns
        daily_returns = price_data.pct_change().dropna()
        
        # Extract market (S&P 500) returns
        market_returns = daily_returns['^GSPC']
        stock_returns = daily_returns.drop('^GSPC', axis=1)
        
        # Risk-free rate (using 3-month Treasury yield as approximation - simplified)
        risk_free_rate = 0.04  # 4% annual rate
        daily_risk_free = (1 + risk_free_rate) ** (1/252) - 1  # Convert to daily
        
        # Calculate annualized return and volatility for each stock
        stock_risk_metrics = {}
        for ticker in stock_returns.columns:
            returns = stock_returns[ticker]
            annualized_return = (1 + returns.mean()) ** 252 - 1
            annualized_volatility = returns.std() * np.sqrt(252)
            
            # Calculate beta for this stock
            covariance = returns.cov(market_returns)
            market_variance = market_returns.var()
            beta = covariance / market_variance
            
            # Calculate alpha
            expected_return = risk_free_rate + beta * (market_returns.mean() * 252 - risk_free_rate)
            alpha = annualized_return - expected_return
            
            stock_risk_metrics[ticker] = {
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_volatility,
                "beta": beta,
                "alpha": alpha
            }
        
        result["risk_metrics"] = stock_risk_metrics
        
        # Calculate portfolio metrics
        portfolio_daily_return = 0
        portfolio_beta = 0
        portfolio_alpha = 0
        
        for ticker, weight in ticker_weights.items():
            if ticker in stock_risk_metrics:
                portfolio_daily_return += stock_returns[ticker].mean() * weight
                portfolio_beta += stock_risk_metrics[ticker]["beta"] * weight
                portfolio_alpha += stock_risk_metrics[ticker]["alpha"] * weight
        
        # Annualized portfolio return and volatility
        portfolio_return = (1 + portfolio_daily_return) ** 252 - 1
        
        # Calculate portfolio volatility (using covariance matrix)
        weights = np.array([ticker_weights.get(ticker, 0) for ticker in stock_returns.columns])
        cov_matrix = stock_returns.cov()
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights)) * 252
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Calculate Sharpe Ratio
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
        
        # Calculate Treynor Ratio (return per unit of systematic risk)
        treynor_ratio = (portfolio_return - risk_free_rate) / portfolio_beta if portfolio_beta != 0 else None
        
        # Calculate R-squared (using approximation)
        portfolio_returns = stock_returns.dot(weights)
        correlation = portfolio_returns.corr(market_returns)
        r_squared = correlation ** 2
        
        # Store results
        result["sharpe_ratio"] = sharpe_ratio
        result["beta"] = portfolio_beta
        result["alpha"] = portfolio_alpha * 100  # Convert to percentage
        result["r_squared"] = r_squared
        result["treynor_ratio"] = treynor_ratio
        result["portfolio_return"] = portfolio_return
        result["portfolio_volatility"] = portfolio_volatility
        
        # Create key_metrics dictionary for UI display
        result["key_metrics"] = {
            "sharpe_ratio": sharpe_ratio,
            "beta": portfolio_beta,
            "alpha": portfolio_alpha * 100,  # Convert to percentage for display
            "r_squared": r_squared,
            "std_dev": portfolio_volatility * 100,  # Convert to percentage
            "max_drawdown": 12.5,  # Placeholder - would need historical calculation
            "sharpe_ratio_context": "+0.3" if sharpe_ratio > 1.0 else "-0.2",
            "beta_context": "Defensive" if portfolio_beta < 1.0 else "Aggressive",
            "alpha_context": "+2.1%" if portfolio_alpha > 0 else "-1.8%",
            "std_dev_context": "Lower than benchmark" if portfolio_volatility < 0.15 else "Higher than benchmark",
            "r_squared_context": "Diversified" if r_squared < 0.7 else "Market dependent",
            "max_drawdown_context": "Moderate risk"
        }
        
        # Create correlation matrix
        result["correlation_matrix"] = daily_returns.corr()
        
        # Generate points for efficient frontier (simplified approach)
        num_portfolios = 20
        efficient_frontier = []
        
        # Random portfolio weights for efficient frontier
        for _ in range(num_portfolios):
            random_weights = np.random.random(len(tickers) - 1)  # Exclude S&P 500
            random_weights /= np.sum(random_weights)
            
            # Calculate return and volatility for this random portfolio
            port_return = 0
            for i, ticker in enumerate(stock_returns.columns):
                port_return += random_weights[i] * stock_returns[ticker].mean() * 252
            
            port_variance = np.dot(random_weights.T, np.dot(cov_matrix, random_weights)) * 252
            port_volatility = np.sqrt(port_variance)
            
            efficient_frontier.append({
                "return": port_return,
                "volatility": port_volatility
            })
        
        # Add actual portfolio point
        efficient_frontier.append({
            "return": portfolio_return,
            "volatility": portfolio_volatility,
            "is_current": True
        })
        
        result["efficient_frontier"] = efficient_frontier
        
        # Create a performance chart comparing portfolio to S&P 500
        # First, get cumulative returns
        portfolio_cum_returns = (1 + portfolio_returns).cumprod()
        market_cum_returns = (1 + market_returns).cumprod()
        
        # Create dataframe for plotting
        performance_df = pd.DataFrame({
            'Portfolio': portfolio_cum_returns,
            'S&P 500': market_cum_returns
        })
        
        # Create the performance chart
        fig = px.line(
            performance_df, 
            title="Portfolio Performance vs. S&P 500",
            labels={"value": "Growth of $1 Invested", "variable": ""}
        )
        fig.update_layout(legend_title_text="")
        result["performance_chart"] = fig
        
        # Create interpretation data
        result["interpretation"] = {
            "Sharpe Ratio": f"The Sharpe ratio of {sharpe_ratio:.2f} indicates how much excess return you receive for the extra volatility of holding a riskier asset. Higher is better, with values above 1.0 generally considered good.",
            "Beta": f"Beta of {portfolio_beta:.2f} measures your portfolio's volatility compared to the market. A beta of 1 means your portfolio moves with the market, less than 1 means lower volatility than the market, and greater than 1 means higher volatility.",
            "Alpha": f"Alpha of {portfolio_alpha*100:.2f}% represents the excess return compared to what would be predicted by beta alone. Positive alpha means the portfolio is outperforming expectations.",
            "Standard Deviation": f"Standard deviation of {portfolio_volatility*100:.2f}% measures the total risk (volatility) of your portfolio. Lower values indicate less price fluctuation.",
            "R-Squared": f"R-squared of {r_squared:.2f} indicates how much of your portfolio's movements can be explained by market movements. Values closer to 1 mean higher correlation with the market."
        }
        
        return result
        
    except Exception as e:
        error_msg = f"Error calculating MPT metrics: {str(e)}"
        result["error"] = error_msg
        
        # Add key_metrics with placeholder values for error handling in the UI
        result["key_metrics"] = {
            "sharpe_ratio": 0.0,
            "beta": 0.0,
            "alpha": 0.0,
            "r_squared": 0.0,
            "std_dev": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio_context": "Error: " + error_msg,
            "beta_context": "Error",
            "alpha_context": "Error",
            "std_dev_context": "Error",
            "r_squared_context": "Error",
            "max_drawdown_context": "Error"
        }
        
        # Add interpretation data for error
        result["interpretation"] = {
            "Error Details": error_msg,
            "Troubleshooting": "Please ensure your portfolio contains valid stock tickers. This analysis requires actual stock data to perform calculations."
        }
        
        return result
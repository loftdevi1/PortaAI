import json
import os
import datetime

from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_investment_recommendations(portfolio, risk_profile, market="US", financial_goals=None):
    """
    Generate personalized investment recommendations using AI based on user portfolio and risk profile.
    
    Args:
        portfolio (list): User's current portfolio
        risk_profile (str): User's risk profile (Low, Medium or High Risk)
        market (str): Target market (US or INDIA)
        financial_goals (list, optional): User's financial goals
        
    Returns:
        dict: AI-generated investment recommendations
    """
    try:
        # Format the portfolio data for the AI
        portfolio_summary = format_portfolio_summary(portfolio)
        
        # Include financial goals if available
        goals_summary = ""
        if financial_goals and len(financial_goals) > 0:
            goals_summary = format_goals_summary(financial_goals)
        
        # Construct the prompt for the AI
        prompt = f"""
        As a financial advisor, analyze this investment portfolio and provide recommendations.
        
        PORTFOLIO DATA:
        {portfolio_summary}
        
        RISK PROFILE: {risk_profile}
        MARKET: {market}
        
        {goals_summary}
        
        Provide the following in JSON format:
        1. A brief assessment of the current portfolio
        2. Three specific investment recommendations with tickers
        3. Long-term strategy suggestions
        4. One area of concern or risk
        
        Response should be valid JSON with these keys: 
        "assessment", "specific_recommendations", "long_term_strategy", "risk_warning"
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Parse the JSON response
        try:
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
        except json.JSONDecodeError:
            # Fallback to text response if JSON parsing fails
            return {
                "assessment": "Unable to provide AI assessment at this time.",
                "specific_recommendations": [],
                "long_term_strategy": "Please try again later.",
                "risk_warning": "AI recommendation service temporarily unavailable."
            }
            
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        return {
            "assessment": "Unable to provide AI assessment at this time.",
            "specific_recommendations": [],
            "long_term_strategy": "Please try again later.",
            "risk_warning": f"Error: {str(e)}"
        }

def generate_tax_optimization_advice(portfolio, country="US"):
    """
    Generate tax optimization advice for the user's portfolio.
    
    Args:
        portfolio (list): User's current portfolio
        country (str): User's country for tax rules (US or INDIA)
        
    Returns:
        dict: Tax optimization recommendations
    """
    try:
        # Format the portfolio data for the AI
        portfolio_summary = format_portfolio_summary(portfolio)
        
        # Current date for tax year reference
        current_year = datetime.datetime.now().year
        
        # Construct the prompt for the AI
        prompt = f"""
        As a tax advisor specializing in investment tax optimization, analyze this portfolio 
        and provide tax-efficient recommendations.
        
        PORTFOLIO DATA:
        {portfolio_summary}
        
        COUNTRY: {country}
        CURRENT TAX YEAR: {current_year}
        
        Provide the following in JSON format:
        1. Tax-loss harvesting opportunities
        2. Tax-advantaged account recommendations
        3. Long-term vs short-term capital gains considerations
        4. Specific tax-efficient investment alternatives
        
        For India, consider STCG, LTCG rules, ELSS funds, and 80C deductions.
        For US, consider 401k, IRA, Roth considerations, wash sale rules, and qualified dividends.
        
        Response should be valid JSON with these keys:
        "tax_loss_harvesting", "tax_advantaged_accounts", "capital_gains_strategy", "tax_efficient_alternatives"
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Parse the JSON response
        try:
            tax_advice = json.loads(response.choices[0].message.content)
            return tax_advice
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "tax_loss_harvesting": "Unable to provide tax-loss harvesting advice at this time.",
                "tax_advantaged_accounts": "Unable to provide tax-advantaged account recommendations.",
                "capital_gains_strategy": "Please consult a tax professional for capital gains strategy.",
                "tax_efficient_alternatives": []
            }
            
    except Exception as e:
        print(f"Error generating tax optimization advice: {e}")
        return {
            "tax_loss_harvesting": "Unable to provide tax-loss harvesting advice at this time.",
            "tax_advantaged_accounts": "Unable to provide tax-advantaged account recommendations.",
            "capital_gains_strategy": "Please consult a tax professional for capital gains strategy.",
            "tax_efficient_alternatives": [],
            "error": str(e)
        }

def format_portfolio_summary(portfolio):
    """Format portfolio data for AI prompt"""
    if not portfolio:
        return "Empty portfolio"
        
    total_value = sum(item.get('amount', 0) for item in portfolio)
    
    summary = f"Total portfolio value: ${total_value:,.2f}\n\n"
    summary += "INVESTMENTS:\n"
    
    for item in portfolio:
        item_type = item.get('type', 'Investment')
        name = item.get('name', 'Unnamed')
        category = item.get('category', 'Uncategorized')
        amount = item.get('amount', 0)
        ticker = item.get('ticker', 'N/A')
        
        summary += f"- {name} ({ticker}): ${amount:,.2f}, Category: {category}, Type: {item_type}\n"
        
        # Add SIP details if applicable
        if item_type == "SIP" and 'monthly_amount' in item and 'months_invested' in item:
            summary += f"  Monthly: ${item['monthly_amount']:,.2f}, Months: {item['months_invested']}\n"
    
    return summary

def format_goals_summary(goals):
    """Format financial goals for AI prompt"""
    if not goals:
        return ""
        
    summary = "FINANCIAL GOALS:\n"
    
    for goal in goals:
        name = goal.get('name', 'Unnamed Goal')
        target = goal.get('target_amount', 0)
        current = goal.get('current_amount', 0)
        years = goal.get('timeline_years', 0)
        risk = goal.get('risk_level', 'Medium')
        
        summary += f"- {name}: Target ${target:,.2f}, Current: ${current:,.2f}, Timeline: {years} years, Risk: {risk}\n"
    
    return summary

def analyze_portfolio_strengths_weaknesses(portfolio, risk_profile):
    """
    Analyze portfolio strengths and weaknesses using AI.
    
    Args:
        portfolio (list): User's current portfolio
        risk_profile (str): User's risk profile
        
    Returns:
        dict: Portfolio SWOT analysis
    """
    try:
        # Format the portfolio data
        portfolio_summary = format_portfolio_summary(portfolio)
        
        # Construct the prompt
        prompt = f"""
        As a portfolio analyst, perform a SWOT analysis on this investment portfolio.
        
        PORTFOLIO DATA:
        {portfolio_summary}
        
        RISK PROFILE: {risk_profile}
        
        Provide a SWOT analysis in JSON format with these keys:
        "strengths", "weaknesses", "opportunities", "threats"
        
        Each section should have 2-3 specific points relevant to this portfolio.
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Parse the JSON response
        try:
            swot_analysis = json.loads(response.choices[0].message.content)
            return swot_analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "strengths": ["Unable to analyze portfolio strengths at this time."],
                "weaknesses": ["Unable to analyze portfolio weaknesses at this time."],
                "opportunities": ["Unable to analyze portfolio opportunities at this time."],
                "threats": ["Unable to analyze portfolio threats at this time."]
            }
            
    except Exception as e:
        print(f"Error analyzing portfolio strengths and weaknesses: {e}")
        return {
            "strengths": ["Unable to analyze portfolio strengths at this time."],
            "weaknesses": ["Unable to analyze portfolio weaknesses at this time."],
            "opportunities": ["Unable to analyze portfolio opportunities at this time."],
            "threats": ["Unable to analyze portfolio threats at this time."],
            "error": str(e)
        }
import pandas as pd
from utils import get_risk_profile_allocation

def analyze_portfolio(portfolio, risk_profile):
    """
    Analyze the current portfolio based on the selected risk profile.
    
    Args:
        portfolio (list): List of portfolio items with name, category, and amount
        risk_profile (str): Selected risk profile
        
    Returns:
        dict: Analysis results including current allocation, target allocation, and insights
    """
    if not portfolio:
        return {
            "current_allocation": {},
            "target_allocation": get_risk_profile_allocation(risk_profile),
            "insights": [{"type": "info", "message": "Add investments to analyze your portfolio."}]
        }
    
    # Calculate current allocation percentages
    total_investment = sum(item['amount'] for item in portfolio)
    
    # Group by category
    current_allocation = {}
    for item in portfolio:
        category = item['category']
        if category not in current_allocation:
            current_allocation[category] = 0
        current_allocation[category] += item['amount']
    
    # Convert to percentages
    current_allocation_pct = {
        category: (amount / total_investment) * 100 
        for category, amount in current_allocation.items()
    }
    
    # Get target allocation for the selected risk profile
    target_allocation = get_risk_profile_allocation(risk_profile)
    
    # Generate insights
    insights = []
    
    # Check for imbalances
    for category, target_pct in target_allocation.items():
        current_pct = current_allocation_pct.get(category, 0)
        
        if category not in current_allocation_pct:
            insights.append({
                "type": "warning",
                "message": f"You have no investments in {category}, which should be {target_pct}% of your portfolio."
            })
        elif abs(current_pct - target_pct) > 10:
            if current_pct > target_pct:
                insights.append({
                    "type": "warning",
                    "message": f"Your {category} allocation ({current_pct:.1f}%) is significantly higher than the recommended {target_pct}%."
                })
            else:
                insights.append({
                    "type": "warning",
                    "message": f"Your {category} allocation ({current_pct:.1f}%) is significantly lower than the recommended {target_pct}%."
                })
        elif abs(current_pct - target_pct) > 5:
            if current_pct > target_pct:
                insights.append({
                    "type": "info",
                    "message": f"Your {category} allocation ({current_pct:.1f}%) is slightly higher than the recommended {target_pct}%."
                })
            else:
                insights.append({
                    "type": "info",
                    "message": f"Your {category} allocation ({current_pct:.1f}%) is slightly lower than the recommended {target_pct}%."
                })
    
    # Check for overconcentration in a single stock
    max_pct_per_stock = {
        "Low Risk (Conservative)": 10,
        "Medium Risk (Balanced)": 15,
        "High Risk (Aggressive)": 20
    }
    
    max_allowed = max_pct_per_stock.get(risk_profile, 15)
    
    for item in portfolio:
        item_pct = (item['amount'] / total_investment) * 100
        if item_pct > max_allowed:
            insights.append({
                "type": "warning",
                "message": f"{item['name']} represents {item_pct:.1f}% of your portfolio, which exceeds the {max_allowed}% recommended maximum for a {risk_profile} profile."
            })
    
    # If no insights, portfolio is well balanced
    if not insights:
        insights.append({
            "type": "success",
            "message": "Your portfolio is well-balanced according to your risk profile."
        })
    
    return {
        "current_allocation": current_allocation_pct,
        "target_allocation": target_allocation,
        "insights": insights
    }

def get_allocation_recommendation(portfolio, analysis_result):
    """
    Generate recommendations for rebalancing the portfolio.
    
    Args:
        portfolio (list): The current portfolio
        analysis_result (dict): Results from portfolio analysis
        
    Returns:
        dict: Recommended actions and allocation
    """
    if not portfolio:
        return {"actions": [], "allocation": {}}
    
    current_allocation = analysis_result["current_allocation"]
    target_allocation = analysis_result["target_allocation"]
    
    total_investment = sum(item['amount'] for item in portfolio)
    
    actions = []
    
    # Calculate the difference between current and target
    for category, target_pct in target_allocation.items():
        current_pct = current_allocation.get(category, 0)
        
        current_amount = total_investment * (current_pct / 100) if current_pct > 0 else 0
        target_amount = total_investment * (target_pct / 100)
        
        difference = target_amount - current_amount
        
        if abs(difference) > total_investment * 0.01:  # More than 1% difference
            if difference > 0:
                actions.append({
                    "category": category,
                    "action_type": "increase",
                    "current_amount": current_amount,
                    "target_amount": target_amount,
                    "difference": difference,
                    "message": f"Increase by ${difference:,.2f} to reach target allocation of {target_pct}%"
                })
            else:
                actions.append({
                    "category": category,
                    "action_type": "decrease",
                    "current_amount": current_amount,
                    "target_amount": target_amount,
                    "difference": difference,
                    "message": f"Decrease by ${abs(difference):,.2f} to reach target allocation of {target_pct}%"
                })
    
    return {
        "actions": actions,
        "total_investment": total_investment
    }

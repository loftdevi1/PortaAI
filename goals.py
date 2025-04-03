import datetime
import os
from database import Base, Session, engine, User, get_session
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Define the financial goal model
class FinancialGoal(Base):
    __tablename__ = 'financial_goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False, default=0.0)
    timeline_years = Column(Integer, nullable=False)
    risk_level = Column(String(50), nullable=False)  # Low, Medium, High
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    target_date = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, name={self.name}, target_amount=${self.target_amount})>"

# Add relationship to User model in database.py
User.goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")

# Database helper functions
def create_financial_goal(user_id, name, description, target_amount, timeline_years, risk_level):
    """Create a new financial goal"""
    session = get_session()
    try:
        # Calculate target date
        target_date = datetime.datetime.utcnow() + datetime.timedelta(days=365 * timeline_years)
        
        goal = FinancialGoal(
            user_id=user_id,
            name=name,
            description=description,
            target_amount=target_amount,
            current_amount=0.0,  # Start with 0
            timeline_years=timeline_years,
            risk_level=risk_level,
            target_date=target_date
        )
        session.add(goal)
        session.commit()
        return goal.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_goals(user_id):
    """Get all financial goals for a user"""
    session = get_session()
    try:
        goals = session.query(FinancialGoal).filter_by(user_id=user_id, is_active=True).all()
        return goals
    finally:
        session.close()

def get_goal_by_id(goal_id):
    """Get goal by ID"""
    session = get_session()
    try:
        goal = session.query(FinancialGoal).filter_by(id=goal_id).first()
        return goal
    finally:
        session.close()

def update_goal_progress(goal_id, current_amount):
    """Update the current amount for a goal"""
    session = get_session()
    try:
        goal = session.query(FinancialGoal).filter_by(id=goal_id).first()
        if goal:
            goal.current_amount = current_amount
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_goal(goal_id):
    """Mark a goal as inactive (soft delete)"""
    session = get_session()
    try:
        goal = session.query(FinancialGoal).filter_by(id=goal_id).first()
        if goal:
            goal.is_active = False
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_goal_risk_level(goal_id, risk_level):
    """Update the risk level for a goal"""
    session = get_session()
    try:
        goal = session.query(FinancialGoal).filter_by(id=goal_id).first()
        if goal:
            goal.risk_level = risk_level
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Goal-based portfolio allocation recommendations
def get_goal_based_allocation(risk_level, timeline_years):
    """
    Get recommended asset allocation based on goal timeline and risk tolerance.
    
    Args:
        risk_level (str): Low, Medium, or High risk tolerance
        timeline_years (int): Number of years until goal target date
        
    Returns:
        dict: Recommended allocation percentages by category
    """
    # Short-term goals (< 5 years)
    if timeline_years < 5:
        if risk_level == "Low":
            return {
                "Large Cap": 30,
                "Mid Cap": 15,
                "Small Cap": 5,
                "Gold": 15,
                "ETFs/Crypto": 5,
                "Bonds/Fixed Income": 30
            }
        elif risk_level == "Medium":
            return {
                "Large Cap": 40,
                "Mid Cap": 20,
                "Small Cap": 10,
                "Gold": 10,
                "ETFs/Crypto": 5,
                "Bonds/Fixed Income": 15
            }
        else:  # High
            return {
                "Large Cap": 40,
                "Mid Cap": 25,
                "Small Cap": 20,
                "Gold": 5,
                "ETFs/Crypto": 10,
                "Bonds/Fixed Income": 0
            }
    
    # Medium-term goals (5-15 years)
    elif timeline_years < 15:
        if risk_level == "Low":
            return {
                "Large Cap": 35,
                "Mid Cap": 20,
                "Small Cap": 10,
                "Gold": 10,
                "ETFs/Crypto": 5,
                "Bonds/Fixed Income": 20
            }
        elif risk_level == "Medium":
            return {
                "Large Cap": 35,
                "Mid Cap": 30,
                "Small Cap": 20,
                "Gold": 5,
                "ETFs/Crypto": 5,
                "Bonds/Fixed Income": 5
            }
        else:  # High
            return {
                "Large Cap": 25,
                "Mid Cap": 30,
                "Small Cap": 30,
                "Gold": 5,
                "ETFs/Crypto": 10,
                "Bonds/Fixed Income": 0
            }
    
    # Long-term goals (15+ years)
    else:
        if risk_level == "Low":
            return {
                "Large Cap": 40,
                "Mid Cap": 25,
                "Small Cap": 15,
                "Gold": 10,
                "ETFs/Crypto": 5,
                "Bonds/Fixed Income": 5
            }
        elif risk_level == "Medium":
            return {
                "Large Cap": 30,
                "Mid Cap": 30,
                "Small Cap": 25,
                "Gold": 5,
                "ETFs/Crypto": 10,
                "Bonds/Fixed Income": 0
            }
        else:  # High
            return {
                "Large Cap": 20,
                "Mid Cap": 30,
                "Small Cap": 35,
                "ETFs/Crypto": 15,
                "Gold": 0,
                "Bonds/Fixed Income": 0
            }

def calculate_monthly_investment_needed(target_amount, current_amount, years, expected_return_rate=0.08):
    """
    Calculate the monthly investment needed to reach a goal.
    
    Args:
        target_amount (float): Target amount to reach
        current_amount (float): Current amount saved
        years (int): Number of years to target date
        expected_return_rate (float): Expected annual return rate (default 8%)
        
    Returns:
        float: Monthly investment needed
    """
    # Convert years to months
    months = years * 12
    
    # Convert annual rate to monthly rate
    monthly_rate = expected_return_rate / 12
    
    # Calculate amount needed to reach goal (future value - present value)
    amount_needed = target_amount - (current_amount * (1 + expected_return_rate) ** years)
    
    # Calculate monthly payment using PMT formula (simplified)
    if monthly_rate == 0:
        return amount_needed / months
    
    monthly_payment = (amount_needed * monthly_rate) / (1 - (1 + monthly_rate) ** -months)
    
    return max(0, monthly_payment)  # Ensure non-negative result

def calculate_goal_progress_percentage(current_amount, target_amount):
    """Calculate the percentage of progress towards a goal"""
    if target_amount <= 0:
        return 0
    
    progress = (current_amount / target_amount) * 100
    return min(100, progress)  # Cap at 100%

def get_expected_return_rate(risk_level):
    """Get expected return rate based on risk level"""
    if risk_level == "Low":
        return 0.06  # 6% annual return
    elif risk_level == "Medium":
        return 0.08  # 8% annual return
    else:  # High
        return 0.10  # 10% annual return
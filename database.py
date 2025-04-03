import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime




# Load environment variables
from dotenv import load_dotenv
load_dotenv()





# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")






# Create database engine with improved connection pooling configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)







Base = declarative_base()

# Create session factory
Session = sessionmaker(bind=engine)

# Helper function to create a new session with retry
def get_session():
    """Get a new session with error handling and connection retry"""
    # Number of retry attempts
    max_retries = 3
    retry_delay = 1  # seconds
    
    # Try to create a session with retries
    for attempt in range(max_retries):
        try:
            session = Session()
            # Test connection with a simple query to ensure it's working
            session.execute(text("SELECT 1"))
            return session
        except Exception as e:
            if attempt < max_retries - 1:
                import time
                print(f"Database connection attempt {attempt+1} failed: {e}. Retrying in {retry_delay} second(s)...")
                time.sleep(retry_delay)
                # Close the session if it was created but connection failed
                if 'session' in locals():
                    try:
                        session.close()
                    except:
                        pass
            else:
                print(f"Error creating database session after {max_retries} attempts: {e}")
                raise

# Define database models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    risk_profile = Column(String(50))
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Portfolio(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    market = Column(String(20), default="INDIA")  # INDIA or US
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    investments = relationship("Investment", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name={self.name})>"


class Investment(Base):
    __tablename__ = 'investments'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    name = Column(String(100), nullable=False)
    ticker = Column(String(50), nullable=True)  # For stocks/ETFs
    category = Column(String(50), nullable=False)  # Large Cap, Mid Cap, etc.
    investment_type = Column(String(20), nullable=False)  # Stock/ETF or SIP
    amount = Column(Float, nullable=False)
    monthly_amount = Column(Float, nullable=True)  # For SIP investments
    months_invested = Column(Integer, nullable=True)  # For SIP investments
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="investments")
    
    def __repr__(self):
        return f"<Investment(id={self.id}, name={self.name}, amount={self.amount})>"


class RecommendationHistory(Base):
    __tablename__ = 'recommendation_history'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    recommendation_date = Column(DateTime, default=datetime.datetime.utcnow)
    current_allocation = Column(Text, nullable=False)  # JSON string
    target_allocation = Column(Text, nullable=False)  # JSON string
    actions = Column(Text, nullable=False)  # JSON string
    
    def __repr__(self):
        return f"<RecommendationHistory(id={self.id}, portfolio_id={self.portfolio_id})>"


# Create all tables
Base.metadata.create_all(engine)

# Database helper functions
def create_user(username, email, password_hash, risk_profile=None):
    """Create a new user"""
    session = get_session()
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            risk_profile=risk_profile
        )
        session.add(user)
        session.commit()
        return user.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_by_username(username):
    """Get user by username"""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        return user
    finally:
        session.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        return user
    finally:
        session.close()

def create_portfolio(user_id, name, description=None, market="INDIA"):
    """Create a new portfolio for a user"""
    session = get_session()
    try:
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            description=description,
            market=market
        )
        session.add(portfolio)
        session.commit()
        return portfolio.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_portfolios(user_id):
    """Get all portfolios for a user"""
    session = get_session()
    try:
        portfolios = session.query(Portfolio).filter_by(user_id=user_id, is_active=True).all()
        return portfolios
    finally:
        session.close()

def get_portfolio_by_id(portfolio_id):
    """Get portfolio by ID"""
    session = get_session()
    try:
        portfolio = session.query(Portfolio).filter_by(id=portfolio_id).first()
        return portfolio
    finally:
        session.close()

def add_investment(portfolio_id, name, category, amount, investment_type, ticker=None, 
                 monthly_amount=None, months_invested=None):
    """Add investment to a portfolio"""
    session = get_session()
    try:
        investment = Investment(
            portfolio_id=portfolio_id,
            name=name,
            ticker=ticker,
            category=category,
            investment_type=investment_type,
            amount=amount,
            monthly_amount=monthly_amount,
            months_invested=months_invested
        )
        session.add(investment)
        session.commit()
        return investment.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_portfolio_investments(portfolio_id):
    """Get all investments in a portfolio"""
    session = get_session()
    try:
        investments = session.query(Investment).filter_by(portfolio_id=portfolio_id).all()
        return investments
    finally:
        session.close()

def save_recommendation(portfolio_id, current_allocation, target_allocation, actions):
    """Save recommendation history for a portfolio"""
    session = get_session()
    try:
        # Convert dictionaries to JSON strings
        current_allocation_json = json.dumps(current_allocation)
        target_allocation_json = json.dumps(target_allocation)
        actions_json = json.dumps(actions)
        
        recommendation = RecommendationHistory(
            portfolio_id=portfolio_id,
            current_allocation=current_allocation_json,
            target_allocation=target_allocation_json,
            actions=actions_json
        )
        session.add(recommendation)
        session.commit()
        return recommendation.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_latest_recommendation(portfolio_id):
    """Get the latest recommendation for a portfolio"""
    session = get_session()
    try:
        recommendation = session.query(RecommendationHistory)\
            .filter_by(portfolio_id=portfolio_id)\
            .order_by(RecommendationHistory.recommendation_date.desc())\
            .first()
        
        if recommendation:
            return {
                'id': recommendation.id,
                'portfolio_id': recommendation.portfolio_id,
                'recommendation_date': recommendation.recommendation_date,
                'current_allocation': json.loads(recommendation.current_allocation),
                'target_allocation': json.loads(recommendation.target_allocation),
                'actions': json.loads(recommendation.actions)
            }
        return None
    finally:
        session.close()
        
def create_goal_based_portfolio(user_id, goal_name, allocation, market="INDIA"):
    """
    Create a new portfolio based on a financial goal
    
    Args:
        user_id (int): The user ID
        goal_name (str): Name of the goal to use for portfolio name
        allocation (dict): Asset allocation dictionary (category -> percentage)
        market (str): Market region (US or INDIA)
        
    Returns:
        int: New portfolio ID
    """
    session = get_session()
    try:
        # Create the portfolio
        portfolio_name = f"Goal Portfolio: {goal_name}"
        portfolio_description = f"Portfolio created for goal: {goal_name}"
        
        portfolio = Portfolio(
            user_id=user_id,
            name=portfolio_name,
            description=portfolio_description,
            market=market
        )
        session.add(portfolio)
        session.flush()  # Get the ID without committing
        
        portfolio_id = portfolio.id
        
        # Create empty investments based on allocation
        for category, percentage in allocation.items():
            # Create a placeholder investment for each category
            investment = Investment(
                portfolio_id=portfolio_id,
                name=f"{category} Allocation",
                category=category,
                investment_type="Stock/ETF",  # Default type
                amount=0  # Start with zero amount
            )
            session.add(investment)
            
        # Save changes
        session.commit()
        return portfolio_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_portfolio(portfolio_id):
    """Mark a portfolio as inactive (soft delete)"""
    session = get_session()
    try:
        portfolio = session.query(Portfolio).filter_by(id=portfolio_id).first()
        if portfolio:
            portfolio.is_active = False
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_investment(investment_id):
    """Delete an investment from a portfolio"""
    session = get_session()
    try:
        investment = session.query(Investment).filter_by(id=investment_id).first()
        if investment:
            session.delete(investment)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_user_risk_profile(user_id, risk_profile):
    """Update a user's risk profile"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.risk_profile = risk_profile
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
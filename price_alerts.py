import os
import datetime
import json
from database import Base, get_session, engine, User, Portfolio, Investment
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Define the alert model
class PriceAlert(Base):
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    investment_id = Column(Integer, ForeignKey('investments.id'), nullable=True)  # Optional link to investment
    ticker = Column(String(50), nullable=False)
    target_price = Column(Float, nullable=False)
    alert_type = Column(String(20), nullable=False)  # 'above' or 'below'
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    phone_number = Column(String(20), nullable=True)  # For SMS alerts
    
    # Relationships
    user = relationship("User", back_populates="price_alerts")
    investment = relationship("Investment", back_populates="alerts")
    
    def __repr__(self):
        return f"<PriceAlert(id={self.id}, ticker={self.ticker}, target_price=${self.target_price})>"

# Add relationships to User and Investment models
User.price_alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
Investment.alerts = relationship("PriceAlert", back_populates="investment", cascade="all, delete-orphan")

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Database helper functions
def create_price_alert(user_id, ticker, target_price, alert_type, investment_id=None, phone_number=None):
    """
    Create a new price alert
    
    Args:
        user_id (int): User ID
        ticker (str): Stock ticker symbol
        target_price (float): Target price to trigger alert
        alert_type (str): 'above' or 'below'
        investment_id (int, optional): Investment ID if linking to portfolio investment
        phone_number (str, optional): Phone number for SMS alerts
        
    Returns:
        int: Alert ID
    """
    session = get_session()
    try:
        # Validate alert type
        if alert_type not in ['above', 'below']:
            raise ValueError("Alert type must be 'above' or 'below'")
            
        # Create alert
        alert = PriceAlert(
            user_id=user_id,
            investment_id=investment_id,
            ticker=ticker,
            target_price=target_price,
            alert_type=alert_type,
            phone_number=phone_number
        )
        session.add(alert)
        session.commit()
        return alert.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_price_alerts(user_id, active_only=True):
    """
    Get all price alerts for a user
    
    Args:
        user_id (int): User ID
        active_only (bool): Only return active alerts if True
        
    Returns:
        list: List of PriceAlert objects
    """
    session = get_session()
    try:
        query = session.query(PriceAlert).filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        alerts = query.all()
        return alerts
    finally:
        session.close()

def delete_price_alert(alert_id):
    """
    Delete (deactivate) a price alert
    
    Args:
        alert_id (int): Alert ID
        
    Returns:
        bool: Success status
    """
    session = get_session()
    try:
        alert = session.query(PriceAlert).filter_by(id=alert_id).first()
        if alert:
            alert.is_active = False
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def mark_alert_triggered(alert_id):
    """
    Mark a price alert as triggered
    
    Args:
        alert_id (int): Alert ID
        
    Returns:
        bool: Success status
    """
    session = get_session()
    try:
        alert = session.query(PriceAlert).filter_by(id=alert_id).first()
        if alert:
            alert.is_triggered = True
            alert.triggered_at = datetime.datetime.utcnow()
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def check_price_alerts(current_prices):
    """
    Check all active price alerts against current prices
    
    Args:
        current_prices (dict): Dictionary of ticker -> current price
        
    Returns:
        list: List of triggered alerts
    """
    session = get_session()
    try:
        # Get all active, untriggered alerts
        alerts = session.query(PriceAlert).filter_by(is_active=True, is_triggered=False).all()
        
        triggered_alerts = []
        
        for alert in alerts:
            if alert.ticker in current_prices:
                current_price = current_prices[alert.ticker]
                
                # Check if alert conditions are met
                is_triggered = False
                if alert.alert_type == 'above' and current_price >= alert.target_price:
                    is_triggered = True
                elif alert.alert_type == 'below' and current_price <= alert.target_price:
                    is_triggered = True
                    
                if is_triggered:
                    # Mark alert as triggered
                    alert.is_triggered = True
                    alert.triggered_at = datetime.datetime.utcnow()
                    triggered_alerts.append({
                        'id': alert.id,
                        'user_id': alert.user_id,
                        'ticker': alert.ticker, 
                        'target_price': alert.target_price,
                        'current_price': current_price,
                        'alert_type': alert.alert_type,
                        'phone_number': alert.phone_number
                    })
        
        # Commit changes if any alerts were triggered
        if triggered_alerts:
            session.commit()
            
        return triggered_alerts
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Function to send SMS alerts using Twilio
def send_sms_price_alerts(triggered_alerts):
    """
    Send SMS notifications for triggered price alerts
    
    Args:
        triggered_alerts (list): List of triggered alert dictionaries
        
    Returns:
        list: List of alerts where SMS was sent successfully
    """
    try:
        # Import send_twilio_message or return empty if not available
        try:
            from send_message import send_twilio_message
        except ImportError:
            print("Twilio not configured, skipping SMS alerts")
            return []
        
        sent_alerts = []
        
        for alert in triggered_alerts:
            if alert.get('phone_number'):
                # Format the message
                direction = "risen above" if alert['alert_type'] == 'above' else "fallen below"
                message = (
                    f"Price Alert: {alert['ticker']} has {direction} your target price of "
                    f"${alert['target_price']:.2f}. Current price: ${alert['current_price']:.2f}"
                )
                
                try:
                    # Send the SMS message
                    send_twilio_message(alert['phone_number'], message)
                    sent_alerts.append(alert)
                except Exception as e:
                    print(f"Error sending SMS alert for {alert['ticker']}: {e}")
        
        return sent_alerts
    except Exception as e:
        print(f"Error in send_sms_price_alerts: {e}")
        return []
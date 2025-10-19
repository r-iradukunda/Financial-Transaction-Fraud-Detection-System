"""
Quick Start Setup Script for MongoDB Database
Run this script to set up the database with sample data
"""

from database import (
    initialize_database,
    FraudTransaction,
    FraudAlert,
    ModelPerformance,
    DailyStatistics
)
from database.config import get_database
from datetime import datetime, timedelta
import random

def create_sample_transactions(count=20):
    """Create sample transactions for testing"""
    print(f"\n📝 Creating {count} sample transactions...")
    
    transaction_types = ['Transfer', 'Withdrawal', 'Deposit', 'Purchase']
    locations = ['New York', 'London', 'Tokyo', 'Singapore', 'Dubai']
    channels = ['Online', 'ATM', 'Branch', 'Mobile']
    occupations = ['Engineer', 'Teacher', 'Doctor', 'Business Owner', 'Student']
    countries = ['USA', 'UK', 'Japan', 'Singapore', 'UAE']
    currencies = ['USD', 'GBP', 'JPY', 'SGD', 'AED']
    
    created_ids = []
    
    for i in range(count):
        # Random transaction data
        is_fraud = random.choice([True, False, False, False])  # 25% fraud rate
        amount = random.uniform(100, 10000) if not is_fraud else random.uniform(5000, 50000)
        
        transaction_data = {
            'TransactionAmount': round(amount, 2),
            'TransactionDate': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%d/%m/%Y %H:%M'),
            'TransactionType': random.choice(transaction_types),
            'Location': random.choice(locations),
            'Channel': random.choice(channels),
            'CustomerAge': random.randint(18, 70),
            'CustomerOccupation': random.choice(occupations),
            'TransactionDuration': random.randint(10, 300),
            'LoginAttempts': random.randint(1, 5) if is_fraud else random.randint(1, 2),
            'AccountBalance': round(random.uniform(1000, 100000), 2),
            'PreviousTransactionDate': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%d/%m/%Y %H:%M'),
            'Sender Country': random.choice(countries),
            'Receiver Country': random.choice(countries),
            'Sender Currency': random.choice(currencies),
            'Receiver Currency': random.choice(currencies),
            'Account Status': 'Active' if not is_fraud else random.choice(['Active', 'Flagged']),
            'Invalid Pin Status': 'Valid' if not is_fraud else random.choice(['Valid', 'Invalid', 'Locked']),
            'Invalid pin retry limits': 3,
            'Invalid pin retry count': random.randint(0, 3) if is_fraud else 0
        }
        
        # Generate prediction data
        if is_fraud:
            probability = random.uniform(60, 95)
            risk_level = 'High' if probability > 75 else 'Medium'
        else:
            probability = random.uniform(5, 40)
            risk_level = 'Low' if probability < 20 else 'Medium'
        
        prediction_data = {
            'is_fraud': is_fraud,
            'probability': round(probability, 2),
            'risk_level': risk_level,
            'confidence': round(100 - probability if not is_fraud else probability, 2),
            'action': 'BLOCK' if (is_fraud and probability > 80) else 'REVIEW' if is_fraud else 'ALLOW'
        }
        
        # Save transaction
        tx_id = FraudTransaction.create(transaction_data, prediction_data)
        created_ids.append((tx_id, is_fraud, probability))
        
        # Create alert for high-risk fraud
        if is_fraud and probability > 75:
            alert_data = {
                'severity': 'critical' if probability > 90 else 'high',
                'fraud_probability': probability / 100,
                'risk_level': risk_level,
                'transaction_amount': amount,
                'customer_info': {
                    'age': transaction_data['CustomerAge'],
                    'occupation': transaction_data['CustomerOccupation']
                },
                'alert_reason': f'High fraud probability: {probability:.2f}%',
                'recommended_action': prediction_data['action']
            }
            FraudAlert.create(tx_id, alert_data)
    
    print(f"✓ Created {count} sample transactions")
    return created_ids

def create_sample_model_performance():
    """Create sample model performance records"""
    print("\n📊 Creating sample model performance records...")
    
    performance_data = {
        'model_version': '1.0',
        'accuracy': 0.94,
        'precision': 0.91,
        'recall': 0.89,
        'f1_score': 0.90,
        'auc_roc': 0.95,
        'confusion_matrix': [[8500, 50], [100, 450]],
        'true_positives': 450,
        'true_negatives': 8500,
        'false_positives': 50,
        'false_negatives': 100,
        'total_predictions': 9100,
        'notes': 'Initial model evaluation'
    }
    
    perf_id = ModelPerformance.create(performance_data)
    print(f"✓ Created model performance record: {perf_id}")
    return perf_id

def calculate_sample_statistics():
    """Calculate statistics for sample data"""
    print("\n📈 Calculating daily statistics...")
    
    from database.utils import DataAggregator
    
    # Calculate stats for today
    today = datetime.now().strftime("%d/%m/%Y")
    stats = DataAggregator.calculate_daily_statistics(today)
    
    if stats:
        print(f"✓ Statistics calculated for {today}")
        print(f"  - Total transactions: {stats['total_transactions']}")
        print(f"  - Fraud detected: {stats['fraud_detected']}")
        print(f"  - Fraud rate: {stats['fraud_percentage']:.2f}%")
    else:
        print("  No transactions found for today")
    
    return stats

def display_database_summary():
    """Display database summary"""
    print("\n" + "="*70)
    print("DATABASE SUMMARY")
    print("="*70)
    
    from database.config import get_collection, Collections
    
    # Count documents in each collection
    collections_info = {
        'Transactions': get_collection(Collections.TRANSACTIONS).count_documents({}),
        'Fraud Alerts': get_collection(Collections.FRAUD_ALERTS).count_documents({}),
        'Model Performance': get_collection(Collections.MODEL_PERFORMANCE).count_documents({}),
        'Daily Statistics': get_collection(Collections.DAILY_STATISTICS).count_documents({}),
        'Audit Logs': get_collection(Collections.AUDIT_LOGS).count_documents({})
    }
    
    print("\nCollection Document Counts:")
    for collection, count in collections_info.items():
        print(f"  - {collection}: {count}")
    
    # Get fraud statistics
    stats = FraudTransaction.get_statistics()
    print(f"\nTransaction Statistics:")
    print(f"  - Total: {stats['total_transactions']}")
    print(f"  - Fraudulent: {stats['fraud_count']}")
    print(f"  - Legitimate: {stats['legitimate_count']}")
    print(f"  - Fraud Rate: {stats['fraud_percentage']:.2f}%")
    
    # Get alert statistics
    alert_stats = FraudAlert.get_alert_statistics()
    print(f"\nAlert Statistics:")
    print(f"  - Total Alerts: {alert_stats['total_alerts']}")
    print(f"  - Pending: {alert_stats['pending_alerts']}")
    print(f"  - Resolved: {alert_stats['resolved_alerts']}")
    
    print("\n" + "="*70)

def main():
    """Main setup function"""
    print("="*70)
    print("FRAUD DETECTION DATABASE - QUICK SETUP")
    print("="*70)
    
    # Step 1: Initialize database
    print("\n1️⃣  Initializing database connection...")
    if not initialize_database():
        print("❌ Failed to connect to database")
        print("\nPlease ensure MongoDB is running:")
        print("  - Local: mongod")
        print("  - Cloud: Check your MongoDB Atlas connection string")
        return
    
    print("✓ Database connected successfully")
    
    # Step 2: Create sample data
    print("\n2️⃣  Creating sample data...")
    create_sample_transactions(count=50)
    create_sample_model_performance()
    
    # Step 3: Calculate statistics
    print("\n3️⃣  Calculating statistics...")
    calculate_sample_statistics()
    
    # Step 4: Display summary
    print("\n4️⃣  Database setup complete!")
    display_database_summary()
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Run the API with database:")
    print("   python app_with_database.py")
    print("\n2. Test database operations:")
    print("   python database_examples.py")
    print("\n3. Access API endpoints:")
    print("   - GET  http://localhost:5000/api/transactions/fraud")
    print("   - GET  http://localhost:5000/api/transactions/all")
    print("   - GET  http://localhost:5000/api/alerts")
    print("   - GET  http://localhost:5000/api/statistics")
    print("   - GET  http://localhost:5000/api/reports/patterns")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

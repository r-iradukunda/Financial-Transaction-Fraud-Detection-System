"""
Example Database Operations
Demonstrates how to use the database for fraud detection system
"""

from database import (
    initialize_database,
    FraudTransaction,
    FraudAlert,
    ModelPerformance,
    DailyStatistics,
    AuditLog
)
from database.utils import ReportGenerator, DataAggregator, SearchUtility, DataValidator
from datetime import datetime

def example_save_transaction():
    """Example: Save a transaction prediction to database"""
    print("\n=== Example: Save Transaction ===")
    
    # Sample transaction data
    transaction_data = {
        'TransactionAmount': 5000.00,
        'TransactionDate': '15/10/2025 14:30',
        'TransactionType': 'Transfer',
        'Location': 'New York',
        'Channel': 'Online',
        'CustomerAge': 35,
        'CustomerOccupation': 'Engineer',
        'TransactionDuration': 120,
        'LoginAttempts': 2,
        'AccountBalance': 10000.00,
        'PreviousTransactionDate': '10/10/2025 10:20',
        'Sender Country': 'USA',
        'Receiver Country': 'Germany',
        'Sender Currency': 'USD',
        'Receiver Currency': 'EUR',
        'Account Status': 'Active',
        'Invalid Pin Status': 'Valid',
        'Invalid pin retry limits': 3,
        'Invalid pin retry count': 0
    }
    
    # Sample prediction data
    prediction_data = {
        'is_fraud': True,
        'probability': 85.5,
        'risk_level': 'High',
        'confidence': 85.5,
        'action': 'REVIEW'
    }
    
    # Save transaction
    transaction_id = FraudTransaction.create(transaction_data, prediction_data)
    print(f"✓ Transaction saved with ID: {transaction_id}")
    
    return transaction_id

def example_create_alert(transaction_id):
    """Example: Create a fraud alert"""
    print("\n=== Example: Create Fraud Alert ===")
    
    alert_data = {
        'severity': 'high',
        'fraud_probability': 0.855,
        'risk_level': 'High',
        'transaction_amount': 5000.00,
        'customer_info': {
            'age': 35,
            'occupation': 'Engineer'
        },
        'alert_reason': 'High fraud probability detected',
        'recommended_action': 'REVIEW'
    }
    
    alert_id = FraudAlert.create(transaction_id, alert_data)
    print(f"✓ Alert created with ID: {alert_id}")
    
    return alert_id

def example_query_fraud_transactions():
    """Example: Query fraudulent transactions"""
    print("\n=== Example: Query Fraudulent Transactions ===")
    
    # Get all fraud transactions
    fraud_transactions = FraudTransaction.find_fraudulent(limit=5)
    print(f"✓ Found {len(fraud_transactions)} fraudulent transactions")
    
    for tx in fraud_transactions:
        print(f"  - Amount: ${tx['transaction_amount']}, Risk: {tx['risk_level']}")
    
    return fraud_transactions

def example_search_transactions():
    """Example: Search transactions with filters"""
    print("\n=== Example: Search Transactions ===")
    
    # Search high-value fraud
    filters = {
        'is_fraud': True,
        'min_amount': 1000,
        'risk_level': 'High',
        'limit': 10
    }
    
    results = SearchUtility.search_transactions(filters)
    print(f"✓ Found {len(results)} high-value fraud transactions")
    
    return results

def example_get_pending_alerts():
    """Example: Get pending fraud alerts"""
    print("\n=== Example: Get Pending Alerts ===")
    
    alerts = FraudAlert.find_pending_alerts(limit=10)
    print(f"✓ Found {len(alerts)} pending alerts")
    
    for alert in alerts:
        print(f"  - Severity: {alert['severity']}, Amount: ${alert.get('transaction_amount', 0)}")
    
    return alerts

def example_update_alert(alert_id):
    """Example: Update alert status"""
    print("\n=== Example: Update Alert Status ===")
    
    FraudAlert.update_alert_status(
        alert_id=alert_id,
        status='resolved',
        reviewed_by='admin_user',
        notes='Verified as false positive after customer contact'
    )
    print(f"✓ Alert {alert_id} updated to 'resolved'")

def example_calculate_daily_stats():
    """Example: Calculate daily statistics"""
    print("\n=== Example: Calculate Daily Statistics ===")
    
    today = datetime.now().strftime("%d/%m/%Y")
    stats = DataAggregator.calculate_daily_statistics(today)
    
    if stats:
        print(f"✓ Daily statistics for {today}:")
        print(f"  - Total transactions: {stats['total_transactions']}")
        print(f"  - Fraud detected: {stats['fraud_detected']}")
        print(f"  - Fraud rate: {stats['fraud_percentage']:.2f}%")
    else:
        print("  No transactions found for today")
    
    return stats

def example_generate_daily_report():
    """Example: Generate daily report"""
    print("\n=== Example: Generate Daily Report ===")
    
    today = datetime.now().strftime("%d/%m/%Y")
    report = ReportGenerator.generate_daily_report(today)
    
    print(f"✓ Daily report generated for {today}")
    print(f"  - Total fraud detected: {report['total_fraud_detected']}")
    print(f"  - Total alerts: {report['total_alerts']}")
    
    return report

def example_fraud_pattern_analysis():
    """Example: Analyze fraud patterns"""
    print("\n=== Example: Fraud Pattern Analysis ===")
    
    report = ReportGenerator.generate_fraud_pattern_report()
    
    print("✓ Fraud pattern analysis complete")
    
    if report['fraud_by_transaction_type']:
        print("\n  Top fraud transaction types:")
        for item in report['fraud_by_transaction_type'][:3]:
            print(f"    - {item['_id']}: {item['count']} cases")
    
    if report['fraud_by_location']:
        print("\n  Top fraud locations:")
        for item in report['fraud_by_location'][:3]:
            print(f"    - {item['_id']}: {item['count']} cases")
    
    return report

def example_get_statistics():
    """Example: Get overall statistics"""
    print("\n=== Example: Overall Statistics ===")
    
    stats = FraudTransaction.get_statistics()
    
    print("✓ Overall transaction statistics:")
    print(f"  - Total transactions: {stats['total_transactions']}")
    print(f"  - Fraud detected: {stats['fraud_count']}")
    print(f"  - Fraud rate: {stats['fraud_percentage']:.2f}%")
    
    alert_stats = FraudAlert.get_alert_statistics()
    
    print("\n✓ Alert statistics:")
    print(f"  - Total alerts: {alert_stats['total_alerts']}")
    print(f"  - Pending: {alert_stats['pending_alerts']}")
    print(f"  - Resolved: {alert_stats['resolved_alerts']}")
    
    return stats, alert_stats

def example_save_model_performance():
    """Example: Save model performance metrics"""
    print("\n=== Example: Save Model Performance ===")
    
    performance_data = {
        'model_version': '1.0',
        'accuracy': 0.94,
        'precision': 0.91,
        'recall': 0.89,
        'f1_score': 0.90,
        'auc_roc': 0.95,
        'true_positives': 450,
        'true_negatives': 8500,
        'false_positives': 50,
        'false_negatives': 100,
        'total_predictions': 9100,
        'confusion_matrix': [[8500, 50], [100, 450]],
        'notes': 'Model evaluation after retraining'
    }
    
    perf_id = ModelPerformance.create(performance_data)
    print(f"✓ Model performance saved with ID: {perf_id}")
    
    return perf_id

def example_audit_log():
    """Example: Create audit log entry"""
    print("\n=== Example: Create Audit Log ===")
    
    log_data = {
        'action_type': 'manual_review',
        'user_id': 'user123',
        'user_name': 'John Doe',
        'target_collection': 'transactions',
        'target_id': 'some_transaction_id',
        'action_details': 'Manually reviewed and approved transaction',
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0'
    }
    
    log_id = AuditLog.create(log_data)
    print(f"✓ Audit log created with ID: {log_id}")
    
    return log_id

def example_data_validation():
    """Example: Validate transaction data"""
    print("\n=== Example: Data Validation ===")
    
    # Valid data
    valid_data = {
        'transaction_amount': 100.0,
        'transaction_date': '15/10/2025 14:30',
        'transaction_type': 'Transfer',
        'customer_age': 30,
        'account_balance': 5000.0
    }
    
    is_valid, message = DataValidator.validate_transaction_data(valid_data)
    print(f"Valid data check: {is_valid} - {message}")
    
    # Invalid data
    invalid_data = {
        'transaction_amount': -100.0,  # Negative amount
        'customer_age': 200  # Invalid age
    }
    
    is_valid, message = DataValidator.validate_transaction_data(invalid_data)
    print(f"Invalid data check: {is_valid} - {message}")

def run_all_examples():
    """Run all examples"""
    print("="*70)
    print("DATABASE OPERATIONS EXAMPLES")
    print("="*70)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to connect to database")
        return
    
    try:
        # 1. Save transaction
        transaction_id = example_save_transaction()
        
        # 2. Create alert
        alert_id = example_create_alert(transaction_id)
        
        # 3. Query transactions
        example_query_fraud_transactions()
        
        # 4. Search transactions
        example_search_transactions()
        
        # 5. Get pending alerts
        alerts = example_get_pending_alerts()
        
        # 6. Update alert (if we have alerts)
        if alert_id:
            example_update_alert(alert_id)
        
        # 7. Calculate daily statistics
        example_calculate_daily_stats()
        
        # 8. Generate reports
        example_generate_daily_report()
        example_fraud_pattern_analysis()
        
        # 9. Get statistics
        example_get_statistics()
        
        # 10. Save model performance
        example_save_model_performance()
        
        # 11. Audit logging
        example_audit_log()
        
        # 12. Data validation
        example_data_validation()
        
        print("\n" + "="*70)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_examples()

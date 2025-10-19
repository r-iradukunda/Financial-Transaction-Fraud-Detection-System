"""
Test script to verify database saving functionality
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:5000/api/predict"

# Test transaction data
test_transaction = {
    "TransactionAmount": 5000.00,
    "TransactionDate": "19/10/2025 23:45",
    "TransactionType": "Transfer",
    "Location": "Chicago",
    "Channel": "Online",
    "CustomerAge": 19,
    "CustomerOccupation": "Student",
    "TransactionDuration": 250,
    "LoginAttempts": 6,
    "AccountBalance": 5500.00,
    "PreviousTransactionDate": "19/10/2025 23:30",
    "Sender Country": "USA",
    "Receiver Country": "Germany",
    "Sender Currency": "USD",
    "Receiver Currency": "EUR",
    "Account Status": "Flagged",
    "Invalid Pin Status": "Locked",
    "Invalid pin retry limits": 3,
    "Invalid pin retry count": 3
}

def test_predict_and_save():
    """Test the prediction endpoint and verify database saving"""
    print("="*70)
    print("TESTING PREDICTION WITH DATABASE SAVE")
    print("="*70)
    
    # Send request
    print("\n1. Sending prediction request...")
    response = requests.post(API_URL, json=test_transaction)
    
    # Check response
    if response.status_code == 200:
        print("✓ Request successful!")
        
        result = response.json()
        
        print("\n2. Response details:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Transaction ID: {result.get('transaction_id')}")
        print(f"   - Alert ID: {result.get('alert_id')}")
        print(f"   - Database save status: {result.get('database_save_status')}")
        
        print("\n3. Prediction results:")
        prediction = result.get('prediction', {})
        print(f"   - Is Fraud: {prediction.get('is_fraud')}")
        print(f"   - Fraud Label: {prediction.get('fraud_label')}")
        print(f"   - Probability: {prediction.get('probability')}%")
        print(f"   - Risk Level: {prediction.get('risk_level')}")
        print(f"   - Confidence: {prediction.get('confidence')}%")
        
        print("\n4. Recommendation:")
        recommendation = result.get('recommendation', {})
        print(f"   - Action: {recommendation.get('action')}")
        print(f"   - Message: {recommendation.get('message')}")
        
        # Check if saved to database
        if result.get('transaction_id'):
            print("\n" + "="*70)
            print("✓ TRANSACTION SUCCESSFULLY SAVED TO DATABASE!")
            print(f"✓ Transaction ID: {result.get('transaction_id')}")
            if result.get('alert_id'):
                print(f"✓ Alert ID: {result.get('alert_id')}")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("⚠ WARNING: Transaction NOT saved to database")
            print(f"Status: {result.get('database_save_status')}")
            print("="*70)
    else:
        print(f"❌ Request failed with status code: {response.status_code}")
        print(f"Error: {response.text}")

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*70)
    print("CHECKING API HEALTH")
    print("="*70)
    
    response = requests.get("http://localhost:5000/api/health")
    
    if response.status_code == 200:
        health = response.json()
        print("\nHealth Status:")
        print(f"   - Status: {health.get('status')}")
        print(f"   - Model loaded: {health.get('model_loaded')}")
        print(f"   - Scaler loaded: {health.get('scaler_loaded')}")
        print(f"   - Encoders loaded: {health.get('encoders_loaded')}")
        print(f"   - Database available: {health.get('database_available')}")
        print(f"   - Database connected: {health.get('database_connected')}")
        
        if not health.get('database_connected'):
            print("\n⚠ WARNING: Database is not connected!")
            print("   Transactions will NOT be saved.")
            print("   Please check:")
            print("   1. MongoDB is running")
            print("   2. Connection string in .env file is correct")
            print("   3. Network connectivity to MongoDB")
        else:
            print("\n✓ Database is connected and ready!")
    else:
        print(f"❌ Health check failed: {response.status_code}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("FRAUD DETECTION DATABASE SAVE TEST")
    print("="*70)
    
    # First check health
    test_health_check()
    
    # Wait for user
    input("\nPress Enter to test prediction with database save...")
    
    # Test prediction
    test_predict_and_save()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

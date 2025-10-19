"""
Fraud Detection Flask API
Complete REST API for fraud detection model
Test with Postman or any HTTP client
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import traceback
import joblib
import os

# Import database modules
try:
    from database import (
        get_database,
        initialize_database,
        FraudTransaction,
        FraudAlert,
        ModelPerformance,
        DailyStatistics,
        AuditLog
    )
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Database modules not available: {e}")
    DATABASE_AVAILABLE = False

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for all routes

# Global variables for model components
model = None
scaler = None
le_dict = None
db_connected = False

# ============================================================================
# LOAD MODELS ON STARTUP
# ============================================================================

import os

def load_models():
    global model, scaler, le_dict
    try:
        # Load model
        model_path = 'fraud_detection_model_decision_tree.joblib'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"{model_path} not found!")
        model = joblib.load(model_path)
        print(f"✓ Model loaded: {model_path}")
        
        # Load scaler
        scaler_path = 'scaler.joblib'
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"{scaler_path} not found!")
        scaler = joblib.load(scaler_path)
        print(f"✓ Scaler loaded: {scaler_path}")
        
        # Load label encoders
        le_path = 'label_encoders.joblib'
        if not os.path.exists(le_path):
            raise FileNotFoundError(f"{le_path} not found!")
        le_dict = joblib.load(le_path)
        print(f"✓ Label encoders loaded: {le_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def init_database():
    """Initialize database connection"""
    global db_connected
    if not DATABASE_AVAILABLE:
        print("⚠ Database modules not available - running without database")
        return False
    
    try:
        db_connected = initialize_database()
        if db_connected:
            print("✓ Database connected successfully")
        else:
            print("⚠ Database connection failed - running without database")
        return db_connected
    except Exception as e:
        print(f"⚠ Database initialization error: {e}")
        return False

# ============================================================================
# PREPROCESSING FUNCTION
# ============================================================================

def preprocess_transaction(data):
    """Preprocess transaction data for prediction"""
    
    # Convert to DataFrame if it's a dict
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()
    
    # Convert dates
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], 
                                           format='%d/%m/%Y %H:%M',
                                           errors='coerce')
    df['PreviousTransactionDate'] = pd.to_datetime(df['PreviousTransactionDate'], 
                                                    format='%d/%m/%Y %H:%M', 
                                                    errors='coerce')
    
    # Extract time features
    df['Hour'] = df['TransactionDate'].dt.hour
    df['DayOfWeek'] = df['TransactionDate'].dt.dayofweek
    df['Month'] = df['TransactionDate'].dt.month
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['IsNightTime'] = ((df['Hour'] >= 22) | (df['Hour'] <= 6)).astype(int)
    
    # Time since previous transaction
    df['HoursSincePrevTransaction'] = (
        (df['TransactionDate'] - df['PreviousTransactionDate']).dt.total_seconds() / 3600
    )
    median_hours = df['HoursSincePrevTransaction'].median()
    if pd.isna(median_hours):
        median_hours = 168
    df['HoursSincePrevTransaction'].fillna(median_hours, inplace=True)
    
    # Additional features
    df['AmountToBalanceRatio'] = df['TransactionAmount'] / (df['AccountBalance'] + 1)
    df['IsCrossBorder'] = (df['Sender Country'] != df['Receiver Country']).astype(int)
    df['IsCurrencyMismatch'] = (df['Sender Currency'] != df['Receiver Currency']).astype(int)
    
    # Encode categorical variables
    categorical_cols = ['TransactionType', 'Location', 'Channel', 
                        'CustomerOccupation', 'Sender Country', 'Receiver Country',
                        'Sender Currency', 'Receiver Currency', 'Account Status',
                        'Invalid Pin Status']
    
    for col in categorical_cols:
        if col in df.columns and col in le_dict:
            known_classes = set(le_dict[col].classes_)
            df[col] = df[col].apply(
                lambda x: x if x in known_classes else le_dict[col].classes_[0]
            )
            df[col] = le_dict[col].transform(df[col].astype(str))
    
    # Drop non-feature columns
    features_to_drop = ['TransactionDate', 'PreviousTransactionDate']
    df = df.drop(features_to_drop, axis=1, errors='ignore')
    
    # Fill any remaining NaN
    df = df.fillna(0)
    
    return df

# ============================================================================
# STATIC FILES & UI
# ============================================================================

@app.route('/', methods=['GET'])
def test_client():
    """Serve the test client interface"""
    return send_from_directory('static', 'index.html')

@app.route('/api', methods=['GET'])
def api_home():
    """API Home - Health Check"""
    return jsonify({
        'status': 'online',
        'message': 'Fraud Detection API is running',
        'version': '1.0',
        'ui': 'Open http://localhost:5000 to test',
        'endpoints': {
            'GET /': 'Test client UI',
            'GET /api': 'API health check',
            'GET /api/health': 'Detailed health status',
            'POST /api/predict': 'Predict single transaction',
            'POST /api/predict/batch': 'Predict multiple transactions',
            'GET /api/model-info': 'Get model information'
        }
    }), 200

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'encoders_loaded': le_dict is not None,
        'database_connected': db_connected,
        'database_available': DATABASE_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    info = {
        'model_type': type(model).__name__,
        'features_count': scaler.n_features_in_ if hasattr(scaler, 'n_features_in_') else 'Unknown',
        'categorical_features': list(le_dict.keys()) if le_dict else [],
        'status': 'ready'
    }
    return jsonify(info), 200

@app.route('/api/predict', methods=['POST'])
def predict_single():
    """
    Predict fraud for a single transaction
    
    Expected JSON format:
    {
        "TransactionAmount": 150.00,
        "TransactionDate": "15/09/2024 14:30",
        "TransactionType": "Withdrawal",
        "Location": "New York",
        "Channel": "ATM",
        "CustomerAge": 35,
        "CustomerOccupation": "Teacher",
        "TransactionDuration": 45,
        "LoginAttempts": 1,
        "AccountBalance": 5000.00,
        "PreviousTransactionDate": "10/09/2024 10:20",
        "Sender Country": "USA",
        "Receiver Country": "USA",
        "Sender Currency": "USD",
        "Receiver Currency": "USD",
        "Account Status": "Active",
        "Invalid Pin Status": "Valid",
        "Invalid pin retry limits": 3,
        "Invalid pin retry count": 0
    }
    """
    
    try:
        # Check if models are loaded
        if model is None or scaler is None or le_dict is None:
            return jsonify({
                'error': 'Models not loaded',
                'message': 'Please ensure all model files are available'
            }), 503
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Please send transaction data as JSON'
            }), 400
        
        # Validate required fields
        required_fields = [
            'TransactionAmount', 'TransactionDate', 'TransactionType',
            'Location', 'Channel', 'CustomerAge', 'CustomerOccupation',
            'TransactionDuration', 'LoginAttempts', 'AccountBalance',
            'PreviousTransactionDate', 'Sender Country', 'Receiver Country',
            'Sender Currency', 'Receiver Currency', 'Account Status',
            'Invalid Pin Status', 'Invalid pin retry limits', 'Invalid pin retry count'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Preprocess the transaction
        processed = preprocess_transaction(data)
        
        # Scale features
        scaled = scaler.transform(processed)
        
        # Make prediction
        prediction = int(model.predict(scaled)[0])
        probability = float(model.predict_proba(scaled)[0][1])
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "Low"
            risk_color = "green"
        elif probability < 0.6:
            risk_level = "Medium"
            risk_color = "yellow"
        else:
            risk_level = "High"
            risk_color = "red"
        
        # Determine action
        if prediction == 1 and probability > 0.7:
            action = "BLOCK"
        elif prediction == 1 or probability > 0.5:
            action = "REVIEW"
        else:
            action = "ALLOW"
        
        # Prepare prediction data for database
        prediction_data = {
            'is_fraud': bool(prediction),
            'probability': round(probability * 100, 2),
            'risk_level': risk_level,
            'confidence': round((1 - probability) * 100, 2) if prediction == 0 else round(probability * 100, 2),
            'action': action
        }
        
        # Save to database if connected
        transaction_id = None
        alert_id = None
        db_save_status = 'not_attempted'
        
        if db_connected and DATABASE_AVAILABLE:
            try:
                # Save transaction to database
                transaction_id = FraudTransaction.create(data, prediction_data)
                db_save_status = 'success'
                print(f"✓ Transaction saved to database with ID: {transaction_id}")
                
                # Create alert if high risk fraud
                if prediction == 1 and probability > 0.7:
                    alert_data = {
                        'severity': 'critical' if probability > 0.9 else 'high',
                        'fraud_probability': probability,
                        'risk_level': risk_level,
                        'transaction_amount': data.get('TransactionAmount'),
                        'customer_info': {
                            'age': data.get('CustomerAge'),
                            'occupation': data.get('CustomerOccupation')
                        },
                        'alert_reason': f'High fraud probability: {probability:.2%}',
                        'recommended_action': action
                    }
                    alert_id = FraudAlert.create(transaction_id, alert_data)
                    print(f"✓ Alert created with ID: {alert_id}")
                
            except Exception as db_error:
                print(f"❌ Database save error: {db_error}")
                db_save_status = f'failed: {str(db_error)}'
        
        # Prepare response
        response = {
            'success': True,
            'transaction_id': transaction_id,
            'alert_id': alert_id,
            'database_save_status': db_save_status,
            'transaction': {
                'amount': data['TransactionAmount'],
                'type': data['TransactionType'],
                'date': data['TransactionDate']
            },
            'prediction': {
                'is_fraud': bool(prediction),
                'fraud_label': 'FRAUD DETECTED' if prediction == 1 else 'LEGITIMATE',
                'probability': round(probability * 100, 2),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'confidence': round((1 - probability) * 100, 2) if prediction == 0 else round(probability * 100, 2)
            },
            'recommendation': {
                'action': action,
                'message': 'Transaction flagged as fraudulent. Immediate review required.' if prediction == 1 
                          else 'Transaction appears legitimate. Safe to proceed.'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict fraud for multiple transactions
    
    Expected JSON format:
    {
        "transactions": [
            {transaction1_data},
            {transaction2_data},
            ...
        ]
    }
    """
    
    try:
        # Check if models are loaded
        if model is None or scaler is None or le_dict is None:
            return jsonify({
                'error': 'Models not loaded',
                'message': 'Please ensure all model files are available'
            }), 503
        
        # Get JSON data
        data = request.get_json()
        
        if not data or 'transactions' not in data:
            return jsonify({
                'error': 'Invalid format',
                'message': 'Please send data in format: {"transactions": [...]}'
            }), 400
        
        transactions = data['transactions']
        
        if not isinstance(transactions, list) or len(transactions) == 0:
            return jsonify({
                'error': 'Invalid transactions',
                'message': 'Transactions must be a non-empty list'
            }), 400
        
        # Process all transactions
        results = []
        
        for idx, transaction in enumerate(transactions):
            try:
                # Preprocess
                processed = preprocess_transaction(transaction)
                scaled = scaler.transform(processed)
                
                # Predict
                prediction = int(model.predict(scaled)[0])
                probability = float(model.predict_proba(scaled)[0][1])
                
                # Risk level
                if probability < 0.3:
                    risk_level = "Low"
                elif probability < 0.6:
                    risk_level = "Medium"
                else:
                    risk_level = "High"
                
                results.append({
                    'transaction_id': idx + 1,
                    'is_fraud': bool(prediction),
                    'fraud_label': 'FRAUD' if prediction == 1 else 'LEGITIMATE',
                    'probability': round(probability * 100, 2),
                    'risk_level': risk_level,
                    'amount': transaction.get('TransactionAmount'),
                    'type': transaction.get('TransactionType')
                })
                
            except Exception as e:
                results.append({
                    'transaction_id': idx + 1,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Summary statistics
        successful = [r for r in results if 'error' not in r]
        fraud_count = sum(1 for r in successful if r['is_fraud'])
        
        response = {
            'success': True,
            'summary': {
                'total_transactions': len(transactions),
                'processed': len(successful),
                'failed': len(transactions) - len(successful),
                'fraud_detected': fraud_count,
                'legitimate': len(successful) - fraud_count,
                'fraud_percentage': round((fraud_count / len(successful) * 100), 2) if successful else 0
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/example', methods=['GET'])
def get_example():
    """Get example transaction JSON for testing"""
    examples = {
        'legitimate_transaction': {
            'TransactionAmount': 150.00,
            'TransactionDate': '15/09/2024 14:30',
            'TransactionType': 'Withdrawal',
            'Location': 'New York',
            'Channel': 'ATM',
            'CustomerAge': 35,
            'CustomerOccupation': 'Teacher',
            'TransactionDuration': 45,
            'LoginAttempts': 1,
            'AccountBalance': 5000.00,
            'PreviousTransactionDate': '10/09/2024 10:20',
            'Sender Country': 'USA',
            'Receiver Country': 'USA',
            'Sender Currency': 'USD',
            'Receiver Currency': 'USD',
            'Account Status': 'Active',
            'Invalid Pin Status': 'Valid',
            'Invalid pin retry limits': 3,
            'Invalid pin retry count': 0
        },
        'suspicious_transaction': {
            'TransactionAmount': 5000.00,
            'TransactionDate': '19/09/2024 23:45',
            'TransactionType': 'Transfer',
            'Location': 'Chicago',
            'Channel': 'Online',
            'CustomerAge': 19,
            'CustomerOccupation': 'Student',
            'TransactionDuration': 250,
            'LoginAttempts': 6,
            'AccountBalance': 5500.00,
            'PreviousTransactionDate': '19/09/2024 23:30',
            'Sender Country': 'USA',
            'Receiver Country': 'Germany',
            'Sender Currency': 'USD',
            'Receiver Currency': 'EUR',
            'Account Status': 'Flagged',
            'Invalid Pin Status': 'Locked',
            'Invalid pin retry limits': 3,
            'Invalid pin retry count': 3
        }
    }
    
    return jsonify({
        'message': 'Example transactions for testing',
        'examples': examples,
        'usage': {
            'single_prediction': 'POST /api/predict with one of the examples',
            'batch_prediction': 'POST /api/predict/batch with {"transactions": [example1, example2]}'
        }
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server',
        'ui': 'Open http://localhost:5000 to access the test interface',
        'available_endpoints': [
            'GET / (UI)',
            'GET /api (API info)',
            'GET /api/health',
            'POST /api/predict',
            'POST /api/predict/batch',
            'GET /api/model-info',
            'GET /api/example'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("FRAUD DETECTION API - STARTING")
    print("="*70)
    
    # Load models on startup
    if not load_models():
        print("\n❌ Failed to load models. Please check model files.")
        exit(1)
    
    print("\n✓ All models loaded successfully!")
    
    # Initialize database
    init_database()
    
    print("\n" + "="*70)
    print("Flask server is ready")
    if db_connected:
        print("Database: CONNECTED - transactions will be saved")
    else:
        print("Database: NOT CONNECTED - transactions will NOT be saved")
    print("="*70 + "\n")
    
    # For production (Render)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
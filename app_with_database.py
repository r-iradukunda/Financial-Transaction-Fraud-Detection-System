"""
Database Integration for Fraud Detection API
Complete Flask API with MongoDB integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import traceback
import joblib
from datetime import datetime

# Import database modules
from database import (
    get_database,
    initialize_database,
    FraudTransaction,
    FraudAlert,
    ModelPerformance,
    DailyStatistics,
    AuditLog
)
from database.utils import ReportGenerator, DataAggregator, SearchUtility
from statistics_api import stats_bp

app = Flask(__name__)
CORS(app)

# Register statistics blueprint
app.register_blueprint(stats_bp)

# Global variables
model = None
scaler = None
le_dict = None
db_connected = False

# ============================================================================
# LOAD MODELS AND INITIALIZE DATABASE
# ============================================================================

import os

def load_models():
    global model, scaler, le_dict
    try:
        model = joblib.load('fraud_detection_model_decision_tree.joblib')
        scaler = joblib.load('scaler.joblib')
        le_dict = joblib.load('label_encoders.joblib')
        print("✓ Models loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def init_database():
    """Initialize database connection"""
    global db_connected
    db_connected = initialize_database()
    if db_connected:
        print("✓ Database connected successfully")
    else:
        print("⚠ Database connection failed - running without database")
    return db_connected

# ============================================================================
# PREPROCESSING FUNCTION
# ============================================================================

def preprocess_transaction(data):
    """Preprocess transaction data for prediction"""
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()
    
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], 
                                           format='%d/%m/%Y %H:%M',
                                           errors='coerce')
    df['PreviousTransactionDate'] = pd.to_datetime(df['PreviousTransactionDate'], 
                                                    format='%d/%m/%Y %H:%M', 
                                                    errors='coerce')
    
    df['Hour'] = df['TransactionDate'].dt.hour
    df['DayOfWeek'] = df['TransactionDate'].dt.dayofweek
    df['Month'] = df['TransactionDate'].dt.month
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['IsNightTime'] = ((df['Hour'] >= 22) | (df['Hour'] <= 6)).astype(int)
    
    df['HoursSincePrevTransaction'] = (
        (df['TransactionDate'] - df['PreviousTransactionDate']).dt.total_seconds() / 3600
    )
    median_hours = df['HoursSincePrevTransaction'].median()
    if pd.isna(median_hours):
        median_hours = 168
    df['HoursSincePrevTransaction'].fillna(median_hours, inplace=True)
    
    df['AmountToBalanceRatio'] = df['TransactionAmount'] / (df['AccountBalance'] + 1)
    df['IsCrossBorder'] = (df['Sender Country'] != df['Receiver Country']).astype(int)
    df['IsCurrencyMismatch'] = (df['Sender Currency'] != df['Receiver Currency']).astype(int)
    
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
    
    features_to_drop = ['TransactionDate', 'PreviousTransactionDate']
    df = df.drop(features_to_drop, axis=1, errors='ignore')
    df = df.fillna(0)
    
    return df

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Fraud Detection API with Database',
        'version': '2.0',
        'database_connected': db_connected,
        'endpoints': {
            'GET /': 'API health check',
            'POST /api/predict': 'Predict single transaction (saves to DB)',
            'GET /api/transactions/fraud': 'Get all fraudulent transactions',
            'GET /api/transactions/all': 'Get all transactions',
            'GET /api/transactions/<id>': 'Get specific transaction',
            'GET /api/alerts': 'Get fraud alerts',
            'POST /api/alerts/<id>/update': 'Update alert status',
            'GET /api/reports/daily/<date>': 'Get daily report (DD/MM/YYYY)',
            'GET /api/reports/patterns': 'Get fraud patterns',
            'GET /api/statistics': 'Get overall statistics',
            'GET /api/search': 'Search transactions with filters',
            'GET /api/stats/dashboard': 'Dashboard statistics (cards data)',
            'GET /api/stats/trends': 'Fraud detection trends over time',
            'GET /api/stats/hotspots': 'Geographic fraud hotspots',
            'GET /api/stats/risk-distribution': 'Risk level distribution',
            'GET /api/stats/transaction-types': 'Statistics by transaction type',
            'GET /api/stats/alerts/summary': 'Fraud alerts summary',
            'GET /api/stats/performance/real-time': 'Real-time model performance',
            'GET /api/stats/recent-transactions': 'Recent transactions list'
        }
    }), 200

@app.route('/api/predict', methods=['POST'])
def predict_single():
    """Predict fraud for a single transaction and save to database"""
    try:
        if model is None or scaler is None or le_dict is None:
            return jsonify({'error': 'Models not loaded'}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Preprocess and predict
        processed = preprocess_transaction(data)
        scaled = scaler.transform(processed)
        prediction = int(model.predict(scaled)[0])
        probability = float(model.predict_proba(scaled)[0][1])
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "Low"
        elif probability < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Determine action
        if prediction == 1 and probability > 0.7:
            action = "BLOCK"
        elif prediction == 1 or probability > 0.5:
            action = "REVIEW"
        else:
            action = "ALLOW"
        
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
        
        if db_connected:
            try:
                # Save transaction
                transaction_id = FraudTransaction.create(data, prediction_data)
                
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
                
            except Exception as db_error:
                print(f"Database error: {db_error}")
        
        response = {
            'success': True,
            'transaction_id': transaction_id,
            'alert_id': alert_id,
            'transaction': {
                'amount': data['TransactionAmount'],
                'type': data['TransactionType'],
                'date': data['TransactionDate']
            },
            'prediction': {
                'is_fraud': bool(prediction),
                'fraud_label': 'FRAUD DETECTED' if prediction == 1 else 'LEGITIMATE',
                'probability': prediction_data['probability'],
                'risk_level': risk_level,
                'confidence': prediction_data['confidence']
            },
            'recommendation': {
                'action': action,
                'message': 'Transaction flagged as fraudulent. Immediate review required.' if prediction == 1 
                          else 'Transaction appears legitimate. Safe to proceed.'
            },
            'timestamp': datetime.now().isoformat(),
            'saved_to_database': db_connected
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/transactions/fraud', methods=['GET'])
def get_fraud_transactions():
    """Get all fraudulent transactions"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        transactions = FraudTransaction.find_fraudulent(limit=limit, skip=skip)
        
        # Convert ObjectId to string
        for t in transactions:
            t['_id'] = str(t['_id'])
        
        return jsonify({
            'success': True,
            'count': len(transactions),
            'transactions': transactions
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/all', methods=['GET'])
def get_all_transactions():
    """Get all transactions"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        transactions = FraudTransaction.find_all(limit=limit, skip=skip)
        
        # Convert ObjectId to string
        for t in transactions:
            t['_id'] = str(t['_id'])
        
        return jsonify({
            'success': True,
            'count': len(transactions),
            'transactions': transactions
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get specific transaction by ID"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        transaction = FraudTransaction.find_by_id(transaction_id)
        
        if transaction:
            transaction['_id'] = str(transaction['_id'])
            return jsonify({
                'success': True,
                'transaction': transaction
            }), 200
        else:
            return jsonify({'error': 'Transaction not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get fraud alerts"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        status = request.args.get('status', 'pending')
        
        if status == 'pending':
            alerts = FraudAlert.find_pending_alerts(limit=50)
        else:
            from database.config import get_collection, Collections
            collection = get_collection(Collections.FRAUD_ALERTS)
            alerts = list(collection.find({'status': status}).limit(50))
        
        # Convert ObjectId to string
        for a in alerts:
            a['_id'] = str(a['_id'])
            if 'transaction_id' in a:
                a['transaction_id'] = str(a['transaction_id'])
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': alerts
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<alert_id>/update', methods=['POST'])
def update_alert(alert_id):
    """Update alert status"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        data = request.get_json()
        status = data.get('status')
        reviewed_by = data.get('reviewed_by', 'admin')
        notes = data.get('notes')
        
        FraudAlert.update_alert_status(alert_id, status, reviewed_by, notes)
        
        return jsonify({
            'success': True,
            'message': 'Alert updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/daily/<date>', methods=['GET'])
def get_daily_report(date):
    """Get daily report for specified date (format: DD/MM/YYYY)"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        report = ReportGenerator.generate_daily_report(date)
        
        # Convert ObjectIds
        for t in report.get('fraud_transactions', []):
            if '_id' in t:
                t['_id'] = str(t['_id'])
        
        for a in report.get('alerts', []):
            if '_id' in a:
                a['_id'] = str(a['_id'])
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/patterns', methods=['GET'])
def get_fraud_patterns():
    """Get fraud pattern analysis"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        report = ReportGenerator.generate_fraud_pattern_report()
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        # Get transaction statistics
        tx_stats = FraudTransaction.get_statistics()
        
        # Get alert statistics
        alert_stats = FraudAlert.get_alert_statistics()
        
        return jsonify({
            'success': True,
            'statistics': {
                'transactions': tx_stats,
                'alerts': alert_stats
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_transactions():
    """Search transactions with filters"""
    if not db_connected:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        filters = {
            'is_fraud': request.args.get('is_fraud', type=lambda x: x.lower() == 'true') if request.args.get('is_fraud') else None,
            'risk_level': request.args.get('risk_level'),
            'min_amount': request.args.get('min_amount', type=float),
            'max_amount': request.args.get('max_amount', type=float),
            'transaction_type': request.args.get('transaction_type'),
            'location': request.args.get('location'),
            'limit': request.args.get('limit', 100, type=int),
            'skip': request.args.get('skip', 0, type=int)
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        results = SearchUtility.search_transactions(filters)
        
        # Convert ObjectIds
        for r in results:
            r['_id'] = str(r['_id'])
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("FRAUD DETECTION API WITH DATABASE - STARTING")
    print("="*70)
    
    # Load models
    if not load_models():
        print("❌ Failed to load models")
        exit(1)
    
    # Initialize database
    init_database()
    
    print("\n✓ System ready!")
    print("="*70 + "\n")
    
    # For production (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

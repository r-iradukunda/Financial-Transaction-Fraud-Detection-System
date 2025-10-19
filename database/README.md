# MongoDB Database Setup for Fraud Detection System

## 📚 Overview

This directory contains the complete MongoDB database implementation for the fraud detection system. It provides a structured way to store transaction predictions, fraud alerts, model performance metrics, and generate comprehensive reports.

## 🗄️ Database Collections

### 1. **transactions**
Stores all transaction predictions and their details.

**Key Fields:**
- Transaction information (amount, date, type, location)
- Customer information (age, occupation, account balance)
- Prediction results (is_fraud, probability, risk_level)
- Geographic data (sender/receiver country, currency)
- Security details (PIN status, login attempts)
- Review status and notes

**Indexes:**
- transaction_date (DESC)
- is_fraud (ASC)
- risk_level (ASC)
- created_at (DESC)

### 2. **fraud_alerts**
High-priority alerts for detected fraud requiring immediate attention.

**Key Fields:**
- Alert severity (low, medium, high, critical)
- Fraud probability and risk level
- Transaction reference
- Review status (pending, investigating, resolved, false_positive)
- Resolution notes

**Indexes:**
- alert_date (DESC)
- status (ASC)
- severity (ASC)

### 3. **model_performance**
Tracks machine learning model performance metrics over time.

**Key Fields:**
- Model version
- Accuracy, precision, recall, F1 score
- Confusion matrix
- True/false positives/negatives
- Evaluation date

**Indexes:**
- evaluation_date (DESC)
- model_version (ASC)

### 4. **daily_statistics**
Aggregated daily statistics for reporting and analysis.

**Key Fields:**
- Total transactions and fraud count
- Transaction amounts (total and fraud)
- Risk level distribution
- Alerts generated
- Fraud percentage

**Indexes:**
- date (DESC, UNIQUE)

### 5. **audit_logs**
Complete audit trail of all system actions.

**Key Fields:**
- Action type and timestamp
- User information
- Target collection and document ID
- Action details
- IP address and user agent

**Indexes:**
- timestamp (DESC)
- action_type (ASC)
- user_id (ASC)

## 📁 File Structure

```
database/
├── __init__.py          # Package initialization
├── config.py            # Database configuration and connection
├── models.py            # Collection models and schemas
└── utils.py             # Utility functions for reports and queries
```

## 🚀 Getting Started

### Installation

1. **Install MongoDB**
   - Local: Download from [MongoDB Official Site](https://www.mongodb.com/try/download/community)
   - Cloud: Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (Free tier available)

2. **Install Python Dependencies**
```bash
pip install pymongo
```

3. **Configure Database Connection**

Edit your environment variables or modify `database/config.py`:

```python
# For local MongoDB
MONGODB_URI = "mongodb://localhost:27017/"

# For MongoDB Atlas (cloud)
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/"

# Database name
DB_NAME = "fraud_detection_db"
```

### Basic Usage

#### 1. Initialize Database Connection

```python
from database import initialize_database

# Initialize connection
if initialize_database():
    print("✓ Database connected")
else:
    print("✗ Database connection failed")
```

#### 2. Save Transaction Prediction

```python
from database import FraudTransaction

# Transaction data
transaction_data = {
    'TransactionAmount': 5000.00,
    'TransactionDate': '15/10/2025 14:30',
    'TransactionType': 'Transfer',
    'Location': 'New York',
    # ... other fields
}

# Prediction results
prediction_data = {
    'is_fraud': True,
    'probability': 85.5,
    'risk_level': 'High',
    'confidence': 85.5,
    'action': 'REVIEW'
}

# Save to database
transaction_id = FraudTransaction.create(transaction_data, prediction_data)
print(f"Transaction saved: {transaction_id}")
```

#### 3. Create Fraud Alert

```python
from database import FraudAlert

alert_data = {
    'severity': 'high',
    'fraud_probability': 0.855,
    'risk_level': 'High',
    'transaction_amount': 5000.00,
    'alert_reason': 'High fraud probability detected',
    'recommended_action': 'REVIEW'
}

alert_id = FraudAlert.create(transaction_id, alert_data)
print(f"Alert created: {alert_id}")
```

#### 4. Query Fraudulent Transactions

```python
from database import FraudTransaction

# Get all fraud transactions
fraud_txs = FraudTransaction.find_fraudulent(limit=100)

# Get transactions by date range
fraud_txs = FraudTransaction.find_by_date_range(
    '01/10/2025 00:00',
    '31/10/2025 23:59'
)

# Get transactions by risk level
high_risk = FraudTransaction.find_by_risk_level('High', limit=50)
```

#### 5. Generate Reports

```python
from database.utils import ReportGenerator

# Daily report
daily_report = ReportGenerator.generate_daily_report('15/10/2025')

# Fraud pattern analysis
pattern_report = ReportGenerator.generate_fraud_pattern_report()

# Model performance report
perf_report = ReportGenerator.generate_model_performance_report()
```

#### 6. Search with Filters

```python
from database.utils import SearchUtility

filters = {
    'is_fraud': True,
    'min_amount': 1000,
    'max_amount': 10000,
    'risk_level': 'High',
    'transaction_type': 'Transfer',
    'location': 'New York',
    'limit': 50
}

results = SearchUtility.search_transactions(filters)
```

## 🔧 API Integration

The database is integrated with the Flask API in `app_with_database.py`.

### Available Endpoints

```
GET  /                              - Health check
POST /api/predict                   - Predict and save transaction
GET  /api/transactions/fraud        - Get fraudulent transactions
GET  /api/transactions/<id>         - Get specific transaction
GET  /api/alerts                    - Get fraud alerts
POST /api/alerts/<id>/update        - Update alert status
GET  /api/reports/daily/<date>      - Get daily report
GET  /api/reports/patterns          - Get fraud patterns
GET  /api/statistics                - Get overall statistics
GET  /api/search                    - Search with filters
```

### Example API Calls

#### Predict and Save Transaction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionAmount": 5000,
    "TransactionDate": "15/10/2025 14:30",
    "TransactionType": "Transfer",
    ...
  }'
```

#### Get Fraudulent Transactions
```bash
curl http://localhost:5000/api/transactions/fraud?limit=10
```

#### Get Daily Report
```bash
curl http://localhost:5000/api/reports/daily/15/10/2025
```

#### Search Transactions
```bash
curl "http://localhost:5000/api/search?is_fraud=true&min_amount=1000&risk_level=High"
```

## 📊 Report Types

### 1. Daily Report
Complete summary of a specific day including:
- Total transactions and fraud count
- Fraud percentage
- List of fraudulent transactions
- Generated alerts

### 2. Weekly Report
Aggregated data for a week:
- Daily breakdown
- Total fraud amount
- Trend analysis

### 3. Fraud Pattern Report
Analysis of fraud patterns:
- Fraud by transaction type
- Fraud by time of day
- Fraud by location
- Cross-border fraud statistics

### 4. Model Performance Report
ML model evaluation metrics:
- Accuracy, precision, recall
- Confusion matrix
- Performance history

## 🛠️ Utility Classes

### ReportGenerator
Generate various types of reports:
- `generate_daily_report(date)`
- `generate_weekly_report(start_date, end_date)`
- `generate_fraud_pattern_report()`
- `generate_model_performance_report()`

### DataAggregator
Aggregate and calculate statistics:
- `calculate_daily_statistics(date)`
- `get_trend_analysis(days)`

### SearchUtility
Advanced search capabilities:
- `search_transactions(filters)`
- `search_high_value_fraud(min_amount)`
- `search_by_customer(age, occupation)`

### DataExporter
Export data in various formats:
- `export_fraud_transactions_to_dict()`
- `export_alerts_to_dict(status)`

### DataValidator
Validate data integrity:
- `validate_transaction_data(data)`
- `check_database_integrity()`

### DataCleanup
Maintenance utilities:
- `archive_old_transactions(days_old)`
- `delete_old_audit_logs(days_old)`

## 📈 Statistics and Monitoring

### Get Transaction Statistics
```python
stats = FraudTransaction.get_statistics()
# Returns: total_transactions, fraud_count, fraud_percentage, risk_distribution
```

### Get Alert Statistics
```python
alert_stats = FraudAlert.get_alert_statistics()
# Returns: total_alerts, pending_alerts, resolved_alerts, etc.
```

### Calculate Daily Statistics
```python
from database.utils import DataAggregator

stats = DataAggregator.calculate_daily_statistics('15/10/2025')
# Automatically saves to daily_statistics collection
```

## 🔐 Security Best Practices

1. **Environment Variables**
   ```bash
   # Create .env file
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
   DB_NAME=fraud_detection_db
   ```

2. **Connection String Security**
   - Never commit connection strings to version control
   - Use environment variables or secret management
   - Enable authentication on MongoDB

3. **Data Privacy**
   - Implement field-level encryption for sensitive data
   - Use MongoDB's built-in encryption at rest
   - Regular security audits via audit_logs

## 🧪 Testing

Run the example script to test all database operations:

```bash
python database_examples.py
```

This will:
- Initialize database connection
- Create sample transactions
- Generate alerts
- Run queries and searches
- Generate reports
- Test all utility functions

## 📝 Schema Validation (Optional)

You can add MongoDB schema validation for data integrity:

```python
# In config.py, add validation rules
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["transaction_amount", "transaction_date", "is_fraud"],
        "properties": {
            "transaction_amount": {
                "bsonType": "double",
                "minimum": 0,
                "description": "must be a positive number"
            },
            "is_fraud": {
                "bsonType": "bool",
                "description": "must be a boolean"
            }
        }
    }
}

db.create_collection("transactions", validator=validator)
```

## 🔄 Backup and Restore

### Backup Database
```bash
mongodump --uri="mongodb://localhost:27017/fraud_detection_db" --out=/backup
```

### Restore Database
```bash
mongorestore --uri="mongodb://localhost:27017/fraud_detection_db" /backup/fraud_detection_db
```

## 📊 Performance Optimization

1. **Indexes**: Already created automatically on connection
2. **Query Optimization**: Use proper filters and limit results
3. **Aggregation Pipeline**: For complex analytics
4. **Connection Pooling**: Handled by PyMongo automatically

## 🐛 Troubleshooting

### Connection Issues
```python
# Test connection
from database.config import DatabaseConfig

config = DatabaseConfig()
if config.connect():
    print("✓ Connected")
else:
    print("✗ Connection failed")
```

### Check Collections
```python
from database import get_database

db = get_database()
collections = db.list_collection_names()
print("Available collections:", collections)
```

### Verify Indexes
```python
collection = get_collection('transactions')
indexes = collection.index_information()
print("Indexes:", indexes)
```

## 📚 Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

## 🤝 Contributing

When adding new features:
1. Update models in `models.py`
2. Add utility functions in `utils.py`
3. Update this README
4. Add examples in `database_examples.py`

## 📄 License

This database module is part of the fraud detection system project.

# QUICK REFERENCE - Database Save Fix

## ✅ What Was Fixed

Your `app.py` now automatically saves all predictions to MongoDB!

## 🚀 Quick Start

```bash
# 1. Start the server
python app.py

# 2. Look for this message:
# "Database: CONNECTED - transactions will be saved" ✓

# 3. Test it
python test_database_save.py
```

## 📊 What Gets Saved Automatically

Every time you call `/api/predict`:
- ✅ Transaction data → `transactions` collection
- ✅ Prediction results → saved with transaction
- ✅ High-risk alert → `fraud_alerts` collection (if probability > 70%)

## 🔍 Check If It's Working

### Method 1: Check API Response
```json
{
  "transaction_id": "67abc123...",  ← Should have a value
  "database_save_status": "success"  ← Should say "success"
}
```

### Method 2: Check MongoDB
```javascript
db.transactions.countDocuments()  // Should increase after each prediction
```

### Method 3: Check Server Logs
```
✓ Transaction saved to database with ID: 67abc123...
```

## ⚠️ Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| `transaction_id` is `null` | Database connection | Verify MongoDB is running |
| `database_save_status: "not_attempted"` | Database modules | Check if `database/` folder exists |
| `database_save_status: "failed: ..."` | Error message | Check the specific error |
| Server says "NOT CONNECTED" | .env file | Verify `MONGODB_URI` is correct |

## 🔗 MongoDB Connection

Your `.env` file should have:
```
MONGODB_URI=mongodb+srv://fab:123@cluster0.iryvt6q.mongodb.net/
DB_NAME=fraud_detection_db
```

## 📝 Response Fields Explained

```json
{
  "transaction_id": "...",        // MongoDB _id of saved transaction
  "alert_id": "...",              // Alert _id (only if high risk)
  "database_save_status": "...",  // "success", "failed: reason", or "not_attempted"
  "prediction": { ... },          // ML model results
  "recommendation": { ... }       // Action to take
}
```

## 🎯 Test Transaction (High Risk)

```json
{
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
```

## ✨ That's It!

Your predictions are now automatically saved to MongoDB! 🎉

For detailed information, see: `DATABASE_SAVE_FIX_GUIDE.md`

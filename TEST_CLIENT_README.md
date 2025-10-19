# Fraud Detection Test Client

## Quick Start

### 1. Start the Flask Application
```bash
python app.py
```

You should see output like:
```
======================================================================
FRAUD DETECTION API - STARTING
======================================================================
✓ Model loaded: fraud_detection_model_decision_tree.joblib
✓ Scaler loaded: scaler.joblib
✓ Label encoders loaded: label_encoders.joblib

✓ All models loaded successfully!

======================================================================
Flask server is ready
======================================================================
```

### 2. Open the Test Client
Open your browser and go to:
```
http://localhost:5000
```

You should see a beautiful fraud detection test interface.

## Features

### Test Interface
- **Clean, minimal design** - Only essential fields and controls
- **Pre-loaded templates** - Quick access to legitimate and suspicious transaction examples
- **Real-time predictions** - Immediate feedback on fraud risk
- **Visual indicators** - Color-coded risk levels (Low/Medium/High)
- **Action recommendations** - ALLOW, REVIEW, or BLOCK

### How to Use

1. **Load a Template** (Optional)
   - Click "Legitimate" or "Suspicious" to auto-fill with example data
   - Or manually enter transaction details

2. **Enter Transaction Data**
   - Fill in all required fields
   - Use DD/MM/YYYY HH:MM format for dates
   - All fields are validated before submission

3. **Submit for Prediction**
   - Click "Predict Fraud Risk" button
   - Wait for the analysis

4. **View Results**
   - See fraud prediction with probability
   - Risk level assessment
   - Recommended action (ALLOW/REVIEW/BLOCK)
   - Confidence score

## API Endpoints

### UI
- `GET /` - Main test interface

### API Info
- `GET /api` - API overview
- `GET /api/health` - Health check
- `GET /api/model-info` - Model details
- `GET /api/example` - Example transactions

### Predictions
- `POST /api/predict` - Single transaction prediction
- `POST /api/predict/batch` - Batch predictions

## Example Transactions

### Legitimate Transaction
- Amount: $150
- Type: Withdrawal
- Location: New York
- Channel: ATM
- Age: 35
- Status: Active
- PIN: Valid

### Suspicious Transaction
- Amount: $5000
- Type: Transfer
- Location: Chicago
- Channel: Online
- Age: 19
- Status: Flagged
- PIN: Locked
- Cross-border: USA → Germany

## Troubleshooting

### Port Already in Use
If port 5000 is already in use:
```bash
python app.py  # Will automatically use next available port
```

### Models Not Found
Make sure these files exist in your project root:
- `fraud_detection_model_decision_tree.joblib`
- `scaler.joblib`
- `label_encoders.joblib`

### CORS Issues
CORS is enabled for all routes, so cross-origin requests should work fine.

## Next Steps

After testing with this interface, you can:
1. Build a full dashboard with analytics
2. Add batch prediction support in the UI
3. Integrate with database to save results
4. Add more visualization options

# Statistics API - Quick Start Guide

## 🚀 Getting Started

### Step 1: Start the Server
```bash
python app_with_database.py
```

The server will start on `http://localhost:5000` (or the configured PORT)

### Step 2: Verify API is Running
Open your browser and go to:
```
http://localhost:5000
```

You should see the API status with all available endpoints.

### Step 3: Test Statistics Endpoints
Run the test script to verify all endpoints:
```bash
python test_statistics_api.py
```

---

## 📊 Quick API Reference

### Get Dashboard Stats (Main Cards)
```bash
curl http://localhost:5000/api/stats/dashboard
```
Returns: Total Transactions, Fraud Detected, Model Accuracy, False Positive Rate

### Get Fraud Trends (Chart Data)
```bash
curl "http://localhost:5000/api/stats/trends?days=7"
```
Returns: Time-series data for Normal, Fraudulent, and Under Review transactions

### Get Fraud Hotspots (Map Data)
```bash
curl http://localhost:5000/api/stats/hotspots
```
Returns: Geographic locations with fraud counts and coordinates

### Get Risk Distribution
```bash
curl http://localhost:5000/api/stats/risk-distribution
```
Returns: Breakdown by Low, Medium, High risk levels

### Get Recent Transactions
```bash
curl "http://localhost:5000/api/stats/recent-transactions?limit=10"
```
Returns: Latest transactions with fraud predictions

---

## 🔌 Frontend Integration

### Simple Fetch Example
```javascript
// Fetch dashboard statistics
fetch('http://localhost:5000/api/stats/dashboard')
  .then(res => res.json())
  .then(data => {
    const cards = data.data.cards;
    console.log('Total Transactions:', cards.total_transactions.value);
    console.log('Fraud Detected:', cards.fraud_detected.value);
    console.log('Model Accuracy:', cards.model_accuracy.value + '%');
  });
```

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function useDashboardStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:5000/api/stats/dashboard')
      .then(res => res.json())
      .then(data => {
        setStats(data.data.cards);
        setLoading(false);
      });
  }, []);

  return { stats, loading };
}

// Use in component
function Dashboard() {
  const { stats, loading } = useDashboardStats();
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Transactions Today: {stats.total_transactions.value}</h1>
      <h2>Fraud Detected: {stats.fraud_detected.value}</h2>
    </div>
  );
}
```

---

## 🎨 Dashboard Implementation Example

### HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>Fraud Detection Dashboard</title>
    <style>
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-change {
            font-size: 0.9em;
        }
        .positive { color: green; }
        .negative { color: red; }
    </style>
</head>
<body>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Transactions</div>
            <div class="stat-value" id="total-transactions">0</div>
            <div class="stat-change" id="total-change">0%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Fraud Detected</div>
            <div class="stat-value" id="fraud-detected">0</div>
            <div class="stat-change" id="fraud-change">0%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Model Accuracy</div>
            <div class="stat-value" id="model-accuracy">0%</div>
            <div class="stat-change" id="accuracy-change">0%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">False Positive Rate</div>
            <div class="stat-value" id="fpr">0%</div>
            <div class="stat-change" id="fpr-change">0%</div>
        </div>
    </div>

    <script src="dashboard.js"></script>
</body>
</html>
```

### JavaScript Implementation
```javascript
// dashboard.js
const API_BASE = 'http://localhost:5000';

async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats/dashboard`);
        const data = await response.json();
        
        if (data.success) {
            const cards = data.data.cards;
            
            // Update Total Transactions
            updateCard('total-transactions', 'total-change', 
                      cards.total_transactions.value, 
                      cards.total_transactions.change);
            
            // Update Fraud Detected
            updateCard('fraud-detected', 'fraud-change', 
                      cards.fraud_detected.value, 
                      cards.fraud_detected.change);
            
            // Update Model Accuracy
            updateCard('model-accuracy', 'accuracy-change', 
                      cards.model_accuracy.value + '%', 
                      cards.model_accuracy.change);
            
            // Update False Positive Rate
            updateCard('fpr', 'fpr-change', 
                      cards.false_positive_rate.value + '%', 
                      cards.false_positive_rate.change);
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

function updateCard(valueId, changeId, value, change) {
    document.getElementById(valueId).textContent = value;
    
    const changeElement = document.getElementById(changeId);
    const isPositive = change > 0;
    
    changeElement.textContent = `${isPositive ? '↑' : '↓'} ${Math.abs(change)}%`;
    changeElement.className = `stat-change ${isPositive ? 'positive' : 'negative'}`;
}

// Load stats on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardStats, 30000);
});
```

---

## 📈 Chart Integration Example

### Using Chart.js
```javascript
async function loadAndDisplayTrends() {
    const response = await fetch('http://localhost:5000/api/stats/trends?days=7');
    const data = await response.json();
    
    const trends = data.data.trends;
    
    const ctx = document.getElementById('trendsChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trends.map(t => t.date_formatted),
            datasets: [
                {
                    label: 'Normal',
                    data: trends.map(t => t.normal),
                    borderColor: 'rgb(34, 197, 94)',
                    tension: 0.4
                },
                {
                    label: 'Fraudulent',
                    data: trends.map(t => t.fraudulent),
                    borderColor: 'rgb(239, 68, 68)',
                    tension: 0.4
                },
                {
                    label: 'Under Review',
                    data: trends.map(t => t.under_review),
                    borderColor: 'rgb(251, 191, 36)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true,
                    text: 'Real-time Fraud Detection Trends'
                }
            }
        }
    });
}
```

---

## 🗺️ Map Integration Example

### Using Leaflet.js
```javascript
async function loadFraudHotspots() {
    const response = await fetch('http://localhost:5000/api/stats/hotspots');
    const data = await response.json();
    
    // Initialize map centered on Rwanda
    const map = L.map('map').setView([-1.9403, 29.8739], 8);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    // Add markers for each hotspot
    data.data.hotspots.forEach(hotspot => {
        const marker = L.marker([
            hotspot.coordinates.lat,
            hotspot.coordinates.lng
        ]).addTo(map);
        
        marker.bindPopup(`
            <b>${hotspot.location}</b><br>
            Fraud Count: ${hotspot.fraud_count}<br>
            Amount: RWF ${hotspot.total_amount.toLocaleString()}
        `);
    });
}
```

---

## 🔄 Auto-Refresh Implementation

```javascript
class DashboardManager {
    constructor(refreshInterval = 30000) {
        this.refreshInterval = refreshInterval;
        this.intervals = [];
    }
    
    start() {
        // Initial load
        this.loadAll();
        
        // Set up auto-refresh
        this.intervals.push(
            setInterval(() => this.loadDashboardStats(), this.refreshInterval),
            setInterval(() => this.loadTrends(), this.refreshInterval),
            setInterval(() => this.loadRecentTransactions(), this.refreshInterval)
        );
        
        console.log('Dashboard auto-refresh started');
    }
    
    stop() {
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
        console.log('Dashboard auto-refresh stopped');
    }
    
    async loadAll() {
        await Promise.all([
            this.loadDashboardStats(),
            this.loadTrends(),
            this.loadRecentTransactions(),
            this.loadHotspots()
        ]);
    }
    
    async loadDashboardStats() {
        const response = await fetch('http://localhost:5000/api/stats/dashboard');
        const data = await response.json();
        // Update dashboard UI
    }
    
    async loadTrends() {
        const response = await fetch('http://localhost:5000/api/stats/trends');
        const data = await response.json();
        // Update trends chart
    }
    
    async loadRecentTransactions() {
        const response = await fetch('http://localhost:5000/api/stats/recent-transactions');
        const data = await response.json();
        // Update transactions table
    }
    
    async loadHotspots() {
        const response = await fetch('http://localhost:5000/api/stats/hotspots');
        const data = await response.json();
        // Update map markers
    }
}

// Usage
const dashboard = new DashboardManager(30000); // Refresh every 30 seconds
dashboard.start();

// Stop when leaving page
window.addEventListener('beforeunload', () => dashboard.stop());
```

---

## ⚡ Performance Tips

1. **Use Pagination**: For large datasets
   ```javascript
   fetch('http://localhost:5000/api/stats/recent-transactions?limit=10')
   ```

2. **Cache Data**: Store frequently accessed data
   ```javascript
   let cachedStats = null;
   let cacheTime = null;
   
   async function getStats() {
       const now = Date.now();
       if (cachedStats && now - cacheTime < 60000) {
           return cachedStats;
       }
       
       const response = await fetch('/api/stats/dashboard');
       cachedStats = await response.json();
       cacheTime = now;
       return cachedStats;
   }
   ```

3. **Debounce Updates**: Prevent excessive API calls
   ```javascript
   function debounce(func, wait) {
       let timeout;
       return function(...args) {
           clearTimeout(timeout);
           timeout = setTimeout(() => func.apply(this, args), wait);
       };
   }
   
   const debouncedUpdate = debounce(loadDashboardStats, 1000);
   ```

---

## 🐛 Troubleshooting

### Server Not Responding
```bash
# Check if server is running
curl http://localhost:5000

# Restart server
python app_with_database.py
```

### Database Connection Issues
```bash
# Test database connection
python test_connection.py

# Check MongoDB status
# For local MongoDB:
sudo systemctl status mongodb
```

### CORS Issues
The API already has CORS enabled. If you still have issues:
```python
# In app_with_database.py
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Empty Data
```bash
# Make sure you have data in database
# Test with sample prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d @sample_transaction.json
```

---

## 📝 Sample Transaction Data

Create `sample_transaction.json`:
```json
{
  "TransactionAmount": 50000,
  "TransactionDate": "19/10/2025 14:30",
  "TransactionType": "Transfer",
  "Location": "Kigali",
  "Channel": "Mobile",
  "CustomerAge": 35,
  "CustomerOccupation": "Business",
  "AccountBalance": 150000,
  "Account Status": "Active",
  "TransactionDuration": 45,
  "LoginAttempts": 1,
  "PreviousTransactionDate": "18/10/2025 10:00",
  "Sender Country": "Rwanda",
  "Receiver Country": "Rwanda",
  "Sender Currency": "RWF",
  "Receiver Currency": "RWF",
  "Invalid Pin Status": "No",
  "Invalid pin retry limits": 3,
  "Invalid pin retry count": 0
}
```

Test it:
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d @sample_transaction.json
```

---

## 🎯 Next Steps

1. **Integrate with your frontend**: Use the provided examples
2. **Customize statistics**: Modify `statistics_api.py` for your needs
3. **Add authentication**: Implement JWT or API keys if needed
4. **Monitor performance**: Track API response times
5. **Set up alerts**: Configure notifications for critical events

---

## 📚 Additional Resources

- Full API Documentation: `STATISTICS_API_DOCUMENTATION.md`
- Test Script: `test_statistics_api.py`
- Main Application: `app_with_database.py`
- Database Models: `database/models.py`

---

## 🆘 Support

If you encounter issues:
1. Check server logs
2. Run `python test_statistics_api.py`
3. Verify database connection
4. Check network/firewall settings

---

**Happy Coding! 🚀**

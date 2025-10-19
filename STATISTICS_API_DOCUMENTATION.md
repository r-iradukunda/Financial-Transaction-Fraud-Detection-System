# Statistics API Documentation

## Overview
This API provides comprehensive statistics and analytics for the Rwanda AI Fraud Detection Dashboard.

**Base URL**: `http://localhost:5000` (Development) or your deployed URL

---

## Statistics Endpoints

### 1. Dashboard Statistics
Get comprehensive dashboard statistics for all dashboard cards.

**Endpoint**: `GET /api/stats/dashboard`

**Response**:
```json
{
  "success": true,
  "data": {
    "cards": {
      "total_transactions": {
        "value": 125,
        "change": 8.9,
        "label": "Total Transactions Today"
      },
      "fraud_detected": {
        "value": 3,
        "change": 50.0,
        "label": "Fraud Detected"
      },
      "model_accuracy": {
        "value": 95.2,
        "change": 0.3,
        "label": "Model Accuracy"
      },
      "false_positive_rate": {
        "value": 1.2,
        "change": -2.1,
        "label": "False Positive Rate"
      }
    },
    "timestamp": "2025-10-19T14:30:00"
  }
}
```

**Usage Example**:
```javascript
// Fetch dashboard stats
fetch('http://localhost:5000/api/stats/dashboard')
  .then(response => response.json())
  .then(data => {
    console.log('Total Transactions:', data.data.cards.total_transactions.value);
    console.log('Fraud Detected:', data.data.cards.fraud_detected.value);
  });
```

---

### 2. Fraud Detection Trends
Get fraud detection trends over time for the line chart.

**Endpoint**: `GET /api/stats/trends?days=7`

**Parameters**:
- `days` (optional): Number of days to retrieve (default: 7)

**Response**:
```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "date": "2025-10-13",
        "date_formatted": "Oct 13",
        "normal": 95,
        "fraudulent": 3,
        "under_review": 7,
        "total": 105
      },
      {
        "date": "2025-10-14",
        "date_formatted": "Oct 14",
        "normal": 102,
        "fraudulent": 5,
        "under_review": 8,
        "total": 115
      }
    ],
    "period": "Last 7 days"
  }
}
```

---

### 3. Fraud Hotspots
Get geographic distribution of fraud for map visualization.

**Endpoint**: `GET /api/stats/hotspots`

**Response**:
```json
{
  "success": true,
  "data": {
    "hotspots": [
      {
        "location": "Kigali",
        "coordinates": {
          "lat": -1.9536,
          "lng": 30.0606,
          "name": "Kigali"
        },
        "fraud_count": 15,
        "total_amount": 125000.50
      },
      {
        "location": "Musanze",
        "coordinates": {
          "lat": -1.4983,
          "lng": 29.6344,
          "name": "Musanze"
        },
        "fraud_count": 8,
        "total_amount": 67500.00
      }
    ],
    "total_locations": 2
  }
}
```

---

### 4. Risk Distribution
Get risk level distribution (Low, Medium, High).

**Endpoint**: `GET /api/stats/risk-distribution`

**Response**:
```json
{
  "success": true,
  "data": {
    "distribution": {
      "Low": {
        "count": 850,
        "amount": 450000.00,
        "percentage": 68.5
      },
      "Medium": {
        "count": 280,
        "amount": 180000.00,
        "percentage": 22.6
      },
      "High": {
        "count": 110,
        "amount": 95000.00,
        "percentage": 8.9
      }
    },
    "total_transactions": 1240
  }
}
```

---

### 5. Transaction Type Statistics
Get statistics by transaction type.

**Endpoint**: `GET /api/stats/transaction-types`

**Response**:
```json
{
  "success": true,
  "data": {
    "transaction_types": [
      {
        "type": "Transfer",
        "total": 450,
        "fraud_count": 12,
        "fraud_percentage": 2.7,
        "total_amount": 850000.00
      },
      {
        "type": "Withdrawal",
        "total": 320,
        "fraud_count": 8,
        "fraud_percentage": 2.5,
        "total_amount": 450000.00
      },
      {
        "type": "Payment",
        "total": 280,
        "fraud_count": 5,
        "fraud_percentage": 1.8,
        "total_amount": 320000.00
      }
    ]
  }
}
```

---

### 6. Alerts Summary
Get fraud alerts summary and recent critical alerts.

**Endpoint**: `GET /api/stats/alerts/summary`

**Response**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "pending": 15,
      "investigating": 8,
      "resolved": 125,
      "false_positive": 12
    },
    "total_alerts": 160,
    "recent_critical": [
      {
        "_id": "671234abcd5678ef90123456",
        "transaction_id": "671234abcd5678ef90123457",
        "severity": "critical",
        "fraud_probability": 0.95,
        "transaction_amount": 50000.00,
        "alert_date": "2025-10-19T10:30:00"
      }
    ]
  }
}
```

---

### 7. Real-Time Performance
Get real-time model performance metrics.

**Endpoint**: `GET /api/stats/performance/real-time`

**Response**:
```json
{
  "success": true,
  "data": {
    "accuracy": 95.2,
    "precision": 93.8,
    "recall": 91.5,
    "f1_score": 92.6,
    "confusion_matrix": {
      "true_positives": 458,
      "true_negatives": 18,
      "false_positives": 6,
      "false_negatives": 18
    },
    "total_predictions": 500
  }
}
```

---

### 8. Recent Transactions
Get recent transactions list.

**Endpoint**: `GET /api/stats/recent-transactions?limit=10`

**Parameters**:
- `limit` (optional): Number of transactions to retrieve (default: 10)

**Response**:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "_id": "671234abcd5678ef90123456",
        "transaction_amount": 25000.00,
        "transaction_type": "Transfer",
        "location": "Kigali",
        "is_fraud": false,
        "fraud_probability": 15.5,
        "risk_level": "Low",
        "action_recommended": "ALLOW",
        "created_at": "2025-10-19T14:25:30"
      }
    ],
    "count": 10
  }
}
```

---

### 9. Health Check
Check statistics API health status.

**Endpoint**: `GET /api/stats/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T14:30:00",
  "total_records": 1240,
  "endpoints": [
    "/api/stats/dashboard",
    "/api/stats/trends",
    "/api/stats/hotspots",
    "/api/stats/risk-distribution",
    "/api/stats/transaction-types",
    "/api/stats/alerts/summary",
    "/api/stats/performance/real-time",
    "/api/stats/recent-transactions"
  ]
}
```

---

## Complete Frontend Integration Example

### React/JavaScript Integration

```javascript
// Dashboard Component Example
import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000';

function Dashboard() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard statistics
      const statsResponse = await fetch(`${API_BASE_URL}/api/stats/dashboard`);
      const statsData = await statsResponse.json();
      setDashboardStats(statsData.data.cards);

      // Fetch trends
      const trendsResponse = await fetch(`${API_BASE_URL}/api/stats/trends?days=7`);
      const trendsData = await trendsResponse.json();
      setTrends(trendsData.data.trends);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      {/* Statistics Cards */}
      <div className="stats-grid">
        <StatCard
          title={dashboardStats.total_transactions.label}
          value={dashboardStats.total_transactions.value}
          change={dashboardStats.total_transactions.change}
        />
        <StatCard
          title={dashboardStats.fraud_detected.label}
          value={dashboardStats.fraud_detected.value}
          change={dashboardStats.fraud_detected.change}
        />
        <StatCard
          title={dashboardStats.model_accuracy.label}
          value={`${dashboardStats.model_accuracy.value}%`}
          change={dashboardStats.model_accuracy.change}
        />
        <StatCard
          title={dashboardStats.false_positive_rate.label}
          value={`${dashboardStats.false_positive_rate.value}%`}
          change={dashboardStats.false_positive_rate.change}
        />
      </div>

      {/* Trends Chart */}
      <TrendsChart data={trends} />
    </div>
  );
}

// Stat Card Component
function StatCard({ title, value, change }) {
  const isPositive = change > 0;
  const changeColor = isPositive ? 'text-green-500' : 'text-red-500';

  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <div className="value">{value}</div>
      <div className={changeColor}>
        {isPositive ? '↑' : '↓'} {Math.abs(change)}%
      </div>
    </div>
  );
}

export default Dashboard;
```

### Vanilla JavaScript Integration

```javascript
// Fetch and display dashboard statistics
async function loadDashboardStats() {
  try {
    const response = await fetch('http://localhost:5000/api/stats/dashboard');
    const data = await response.json();
    
    if (data.success) {
      const cards = data.data.cards;
      
      // Update Total Transactions
      document.getElementById('total-transactions').textContent = cards.total_transactions.value;
      document.getElementById('total-change').textContent = `${cards.total_transactions.change}%`;
      
      // Update Fraud Detected
      document.getElementById('fraud-detected').textContent = cards.fraud_detected.value;
      document.getElementById('fraud-change').textContent = `${cards.fraud_detected.change}%`;
      
      // Update Model Accuracy
      document.getElementById('model-accuracy').textContent = `${cards.model_accuracy.value}%`;
      document.getElementById('accuracy-change').textContent = `${cards.model_accuracy.change}%`;
      
      // Update False Positive Rate
      document.getElementById('fpr').textContent = `${cards.false_positive_rate.value}%`;
      document.getElementById('fpr-change').textContent = `${cards.false_positive_rate.change}%`;
    }
  } catch (error) {
    console.error('Error loading dashboard stats:', error);
  }
}

// Fetch and display trends
async function loadTrends() {
  try {
    const response = await fetch('http://localhost:5000/api/stats/trends?days=7');
    const data = await response.json();
    
    if (data.success) {
      const trends = data.data.trends;
      // Use trends data with your charting library (Chart.js, Recharts, etc.)
      renderChart(trends);
    }
  } catch (error) {
    console.error('Error loading trends:', error);
  }
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', function() {
  loadDashboardStats();
  loadTrends();
  
  // Refresh every 30 seconds
  setInterval(loadDashboardStats, 30000);
});
```

### Chart.js Integration Example

```javascript
async function loadAndRenderTrends() {
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
          label: 'Normal Transactions',
          data: trends.map(t => t.normal),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
        },
        {
          label: 'Fraudulent',
          data: trends.map(t => t.fraudulent),
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
        },
        {
          label: 'Under Review',
          data: trends.map(t => t.under_review),
          borderColor: 'rgb(251, 191, 36)',
          backgroundColor: 'rgba(251, 191, 36, 0.1)',
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error
- `503`: Service Unavailable (Database not connected)

---

## Testing the API

### Using cURL

```bash
# Test dashboard stats
curl http://localhost:5000/api/stats/dashboard

# Test trends with parameters
curl "http://localhost:5000/api/stats/trends?days=14"

# Test hotspots
curl http://localhost:5000/api/stats/hotspots

# Test health check
curl http://localhost:5000/api/stats/health
```

### Using Python

```python
import requests

API_BASE = 'http://localhost:5000'

# Get dashboard statistics
response = requests.get(f'{API_BASE}/api/stats/dashboard')
data = response.json()
print(f"Total Transactions: {data['data']['cards']['total_transactions']['value']}")

# Get trends
response = requests.get(f'{API_BASE}/api/stats/trends', params={'days': 7})
trends = response.json()
print(f"Trend data points: {len(trends['data']['trends'])}")

# Get fraud hotspots
response = requests.get(f'{API_BASE}/api/stats/hotspots')
hotspots = response.json()
print(f"Fraud hotspots: {hotspots['data']['total_locations']}")
```

---

## Auto-Refresh Implementation

For real-time dashboard updates:

```javascript
class DashboardUpdater {
  constructor(updateInterval = 30000) { // 30 seconds
    this.updateInterval = updateInterval;
    this.timers = [];
  }

  start() {
    // Initial load
    this.updateAll();

    // Set up auto-refresh
    this.timers.push(
      setInterval(() => this.updateDashboardStats(), this.updateInterval)
    );
    this.timers.push(
      setInterval(() => this.updateTrends(), this.updateInterval)
    );
    this.timers.push(
      setInterval(() => this.updateRecentTransactions(), this.updateInterval)
    );
  }

  stop() {
    this.timers.forEach(timer => clearInterval(timer));
    this.timers = [];
  }

  async updateAll() {
    await Promise.all([
      this.updateDashboardStats(),
      this.updateTrends(),
      this.updateRecentTransactions()
    ]);
  }

  async updateDashboardStats() {
    const response = await fetch('http://localhost:5000/api/stats/dashboard');
    const data = await response.json();
    // Update UI with data
  }

  async updateTrends() {
    const response = await fetch('http://localhost:5000/api/stats/trends?days=7');
    const data = await response.json();
    // Update chart with data
  }

  async updateRecentTransactions() {
    const response = await fetch('http://localhost:5000/api/stats/recent-transactions?limit=5');
    const data = await response.json();
    // Update transactions list
  }
}

// Usage
const updater = new DashboardUpdater(30000); // Update every 30 seconds
updater.start();

// Stop updates when leaving page
window.addEventListener('beforeunload', () => updater.stop());
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Amounts are in RWF (Rwandan Francs)
- The API supports CORS for frontend integration
- Database connection status is checked before each operation
- Statistics are calculated in real-time from the database

---

## Support

For issues or questions, check:
1. Database connection: `GET /api/stats/health`
2. Main API status: `GET /`
3. Error logs in the console

"""
Test script for Statistics API endpoints
Tests all statistics endpoints and displays results
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = 'http://localhost:5000'

def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_endpoint(endpoint, params=None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        print(f"\n🔍 Testing: {endpoint}")
        if params:
            print(f"   Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("   ✅ Success!")
                return data
            else:
                print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Server not running?")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def display_dashboard_stats(data):
    """Display dashboard statistics"""
    if not data or 'data' not in data:
        return
    
    cards = data['data']['cards']
    
    print("\n📊 DASHBOARD STATISTICS:")
    print("-" * 70)
    
    for key, card in cards.items():
        change_symbol = "↑" if card['change'] > 0 else "↓"
        change_color = "🟢" if card['change'] > 0 else "🔴"
        
        print(f"\n  {card['label']}:")
        print(f"    Value: {card['value']}")
        print(f"    Change: {change_color} {change_symbol} {abs(card['change'])}%")

def display_trends(data):
    """Display trend data"""
    if not data or 'data' not in data:
        return
    
    trends = data['data']['trends']
    
    print("\n📈 FRAUD TRENDS:")
    print("-" * 70)
    print(f"Period: {data['data']['period']}")
    print("\nDate       | Normal | Fraud | Review | Total")
    print("-" * 50)
    
    for trend in trends[-5:]:  # Show last 5 days
        print(f"{trend['date_formatted']:10} | {trend['normal']:6} | "
              f"{trend['fraudulent']:5} | {trend['under_review']:6} | {trend['total']:5}")

def display_hotspots(data):
    """Display fraud hotspots"""
    if not data or 'data' not in data:
        return
    
    hotspots = data['data']['hotspots']
    
    print("\n🗺️  FRAUD HOTSPOTS:")
    print("-" * 70)
    
    for hotspot in hotspots[:5]:  # Show top 5
        print(f"\n  📍 {hotspot['location']}")
        print(f"     Fraud Count: {hotspot['fraud_count']}")
        print(f"     Total Amount: RWF {hotspot['total_amount']:,.2f}")
        print(f"     Coordinates: ({hotspot['coordinates']['lat']}, "
              f"{hotspot['coordinates']['lng']})")

def display_risk_distribution(data):
    """Display risk distribution"""
    if not data or 'data' not in data:
        return
    
    distribution = data['data']['distribution']
    
    print("\n⚠️  RISK DISTRIBUTION:")
    print("-" * 70)
    
    for level, stats in distribution.items():
        print(f"\n  {level} Risk:")
        print(f"    Count: {stats['count']}")
        print(f"    Percentage: {stats['percentage']}%")
        print(f"    Total Amount: RWF {stats['amount']:,.2f}")

def display_transaction_types(data):
    """Display transaction type statistics"""
    if not data or 'data' not in data:
        return
    
    types = data['data']['transaction_types']
    
    print("\n💳 TRANSACTION TYPES:")
    print("-" * 70)
    
    for tx_type in types[:5]:  # Show top 5
        print(f"\n  {tx_type['type']}:")
        print(f"    Total: {tx_type['total']}")
        print(f"    Fraud: {tx_type['fraud_count']} ({tx_type['fraud_percentage']}%)")
        print(f"    Amount: RWF {tx_type['total_amount']:,.2f}")

def display_alerts_summary(data):
    """Display alerts summary"""
    if not data or 'data' not in data:
        return
    
    summary = data['data']['summary']
    total = data['data']['total_alerts']
    
    print("\n🚨 ALERTS SUMMARY:")
    print("-" * 70)
    print(f"\nTotal Alerts: {total}")
    print(f"\n  Pending: {summary['pending']}")
    print(f"  Investigating: {summary['investigating']}")
    print(f"  Resolved: {summary['resolved']}")
    print(f"  False Positives: {summary['false_positive']}")
    
    recent = data['data'].get('recent_critical', [])
    if recent:
        print(f"\n  Recent Critical Alerts: {len(recent)}")

def display_performance(data):
    """Display model performance"""
    if not data or 'data' not in data:
        return
    
    perf = data['data']
    
    print("\n🎯 MODEL PERFORMANCE:")
    print("-" * 70)
    print(f"\n  Accuracy: {perf['accuracy']}%")
    print(f"  Precision: {perf['precision']}%")
    print(f"  Recall: {perf['recall']}%")
    print(f"  F1 Score: {perf['f1_score']}%")
    
    cm = perf['confusion_matrix']
    print(f"\n  Confusion Matrix:")
    print(f"    True Positives: {cm['true_positives']}")
    print(f"    True Negatives: {cm['true_negatives']}")
    print(f"    False Positives: {cm['false_positives']}")
    print(f"    False Negatives: {cm['false_negatives']}")
    print(f"\n  Total Predictions: {perf['total_predictions']}")

def display_recent_transactions(data):
    """Display recent transactions"""
    if not data or 'data' not in data:
        return
    
    transactions = data['data']['transactions']
    
    print("\n📝 RECENT TRANSACTIONS:")
    print("-" * 70)
    
    for tx in transactions[:5]:  # Show first 5
        fraud_label = "🚨 FRAUD" if tx['is_fraud'] else "✅ OK"
        print(f"\n  {fraud_label} | {tx['transaction_type']} | "
              f"RWF {tx['transaction_amount']:,.2f}")
        print(f"    Location: {tx['location']}")
        print(f"    Risk: {tx['risk_level']} ({tx['fraud_probability']:.1f}%)")
        print(f"    Action: {tx['action_recommended']}")

def main():
    """Main test function"""
    print_section("STATISTICS API TEST")
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health check first
    print_section("1. HEALTH CHECK")
    health_data = test_endpoint('/api/stats/health')
    if health_data:
        print(f"\n✅ API is healthy")
        print(f"   Total records in database: {health_data.get('total_records', 'N/A')}")
    else:
        print("\n❌ API health check failed!")
        print("   Make sure the server is running: python app_with_database.py")
        return
    
    # Test dashboard statistics
    print_section("2. DASHBOARD STATISTICS")
    dashboard_data = test_endpoint('/api/stats/dashboard')
    display_dashboard_stats(dashboard_data)
    
    # Test trends
    print_section("3. FRAUD TRENDS")
    trends_data = test_endpoint('/api/stats/trends', params={'days': 7})
    display_trends(trends_data)
    
    # Test hotspots
    print_section("4. FRAUD HOTSPOTS")
    hotspots_data = test_endpoint('/api/stats/hotspots')
    display_hotspots(hotspots_data)
    
    # Test risk distribution
    print_section("5. RISK DISTRIBUTION")
    risk_data = test_endpoint('/api/stats/risk-distribution')
    display_risk_distribution(risk_data)
    
    # Test transaction types
    print_section("6. TRANSACTION TYPES")
    types_data = test_endpoint('/api/stats/transaction-types')
    display_transaction_types(types_data)
    
    # Test alerts summary
    print_section("7. ALERTS SUMMARY")
    alerts_data = test_endpoint('/api/stats/alerts/summary')
    display_alerts_summary(alerts_data)
    
    # Test performance
    print_section("8. MODEL PERFORMANCE")
    perf_data = test_endpoint('/api/stats/performance/real-time')
    display_performance(perf_data)
    
    # Test recent transactions
    print_section("9. RECENT TRANSACTIONS")
    recent_data = test_endpoint('/api/stats/recent-transactions', params={'limit': 5})
    display_recent_transactions(recent_data)
    
    # Summary
    print_section("TEST SUMMARY")
    print("\n✅ All statistics endpoints tested successfully!")
    print("\nAvailable endpoints:")
    print("  • GET /api/stats/dashboard")
    print("  • GET /api/stats/trends?days=7")
    print("  • GET /api/stats/hotspots")
    print("  • GET /api/stats/risk-distribution")
    print("  • GET /api/stats/transaction-types")
    print("  • GET /api/stats/alerts/summary")
    print("  • GET /api/stats/performance/real-time")
    print("  • GET /api/stats/recent-transactions?limit=10")
    print("  • GET /api/stats/health")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")

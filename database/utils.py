"""
Database Utility Functions
Helper functions for common database operations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .config import get_collection, Collections
from .models import FraudTransaction, FraudAlert, DailyStatistics, AuditLog
import pymongo

# ============================================================================
# REPORT GENERATION UTILITIES
# ============================================================================

class ReportGenerator:
    """Generate various reports from stored data"""
    
    @staticmethod
    def generate_daily_report(date: str) -> Dict:
        """Generate comprehensive daily report"""
        # Get daily statistics
        daily_stats = DailyStatistics.get_by_date(date)
        
        # Get fraud transactions for the day
        fraud_transactions = FraudTransaction.find_by_date_range(
            f"{date} 00:00",
            f"{date} 23:59"
        )
        
        # Get alerts for the day
        alerts_collection = get_collection(Collections.FRAUD_ALERTS)
        alerts = list(alerts_collection.find({
            "alert_date": {
                "$gte": datetime.strptime(date, "%d/%m/%Y"),
                "$lt": datetime.strptime(date, "%d/%m/%Y") + timedelta(days=1)
            }
        }))
        
        return {
            "report_date": date,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": daily_stats if daily_stats else {},
            "fraud_transactions": fraud_transactions,
            "alerts": alerts,
            "total_fraud_detected": len([t for t in fraud_transactions if t.get("is_fraud")]),
            "total_alerts": len(alerts)
        }
    
    @staticmethod
    def generate_weekly_report(start_date: str, end_date: str) -> Dict:
        """Generate weekly summary report"""
        daily_stats = DailyStatistics.get_date_range(start_date, end_date)
        
        total_transactions = sum(d.get("total_transactions", 0) for d in daily_stats)
        total_fraud = sum(d.get("fraud_detected", 0) for d in daily_stats)
        total_amount = sum(d.get("total_amount", 0) for d in daily_stats)
        fraud_amount = sum(d.get("fraud_amount", 0) for d in daily_stats)
        
        return {
            "report_type": "weekly",
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_transactions": total_transactions,
                "fraud_detected": total_fraud,
                "legitimate_transactions": total_transactions - total_fraud,
                "fraud_percentage": (total_fraud / total_transactions * 100) if total_transactions > 0 else 0,
                "total_transaction_amount": total_amount,
                "fraud_amount": fraud_amount,
                "fraud_amount_percentage": (fraud_amount / total_amount * 100) if total_amount > 0 else 0
            },
            "daily_breakdown": daily_stats
        }
    
    @staticmethod
    def generate_fraud_pattern_report() -> Dict:
        """Analyze fraud patterns"""
        collection = get_collection(Collections.TRANSACTIONS)
        
        # Fraud by transaction type
        fraud_by_type = list(collection.aggregate([
            {"$match": {"is_fraud": True}},
            {
                "$group": {
                    "_id": "$transaction_type",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$transaction_amount"}
                }
            },
            {"$sort": {"count": -1}}
        ]))
        
        # Fraud by time of day
        fraud_by_hour = list(collection.aggregate([
            {"$match": {"is_fraud": True}},
            {
                "$project": {
                    "hour": {"$hour": "$created_at"}
                }
            },
            {
                "$group": {
                    "_id": "$hour",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]))
        
        # Fraud by location
        fraud_by_location = list(collection.aggregate([
            {"$match": {"is_fraud": True}},
            {
                "$group": {
                    "_id": "$location",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))
        
        # Cross-border fraud
        cross_border_fraud = collection.count_documents({
            "is_fraud": True,
            "is_cross_border": True
        })
        
        total_fraud = collection.count_documents({"is_fraud": True})
        
        return {
            "report_type": "fraud_patterns",
            "generated_at": datetime.utcnow().isoformat(),
            "fraud_by_transaction_type": fraud_by_type,
            "fraud_by_hour": fraud_by_hour,
            "fraud_by_location": fraud_by_location,
            "cross_border_fraud": {
                "count": cross_border_fraud,
                "percentage": (cross_border_fraud / total_fraud * 100) if total_fraud > 0 else 0
            }
        }
    
    @staticmethod
    def generate_model_performance_report() -> Dict:
        """Generate model performance report"""
        from .models import ModelPerformance
        
        latest_performance = ModelPerformance.get_latest_performance()
        history = ModelPerformance.get_performance_history(limit=5)
        
        return {
            "report_type": "model_performance",
            "generated_at": datetime.utcnow().isoformat(),
            "latest_metrics": latest_performance,
            "performance_history": history
        }

# ============================================================================
# DATA AGGREGATION UTILITIES
# ============================================================================

class DataAggregator:
    """Aggregate and summarize data"""
    
    @staticmethod
    def calculate_daily_statistics(date: str):
        """Calculate and store daily statistics"""
        collection = get_collection(Collections.TRANSACTIONS)
        
        # Parse date
        start_datetime = datetime.strptime(f"{date} 00:00", "%d/%m/%Y %H:%M")
        end_datetime = datetime.strptime(f"{date} 23:59", "%d/%m/%Y %H:%M")
        
        # Query for transactions on this date
        query = {
            "created_at": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        }
        
        # Get all transactions for the day
        transactions = list(collection.find(query))
        
        if not transactions:
            return None
        
        # Calculate statistics
        total_transactions = len(transactions)
        fraud_transactions = [t for t in transactions if t.get("is_fraud")]
        fraud_count = len(fraud_transactions)
        
        total_amount = sum(t.get("transaction_amount", 0) for t in transactions)
        fraud_amount = sum(t.get("transaction_amount", 0) for t in fraud_transactions)
        
        high_risk = len([t for t in transactions if t.get("risk_level") == "High"])
        medium_risk = len([t for t in transactions if t.get("risk_level") == "Medium"])
        low_risk = len([t for t in transactions if t.get("risk_level") == "Low"])
        
        # Count alerts generated on this day
        alerts_collection = get_collection(Collections.FRAUD_ALERTS)
        alerts_count = alerts_collection.count_documents({
            "alert_date": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        })
        
        # Store statistics
        stats = {
            "total_transactions": total_transactions,
            "fraud_detected": fraud_count,
            "legitimate_transactions": total_transactions - fraud_count,
            "fraud_percentage": (fraud_count / total_transactions * 100) if total_transactions > 0 else 0,
            "total_amount": total_amount,
            "fraud_amount": fraud_amount,
            "high_risk_transactions": high_risk,
            "medium_risk_transactions": medium_risk,
            "low_risk_transactions": low_risk,
            "alerts_generated": alerts_count
        }
        
        DailyStatistics.create_or_update(date, stats)
        
        return stats
    
    @staticmethod
    def get_trend_analysis(days: int = 30) -> Dict:
        """Get trend analysis for the past N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        collection = get_collection(Collections.TRANSACTIONS)
        
        # Aggregate by day
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "total": {"$sum": 1},
                    "fraud_count": {
                        "$sum": {"$cond": ["$is_fraud", 1, 0]}
                    },
                    "total_amount": {"$sum": "$transaction_amount"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        return {
            "period_days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily_trends": results
        }

# ============================================================================
# SEARCH AND QUERY UTILITIES
# ============================================================================

class SearchUtility:
    """Advanced search and query utilities"""
    
    @staticmethod
    def search_transactions(filters: Dict) -> List[Dict]:
        """Search transactions with multiple filters"""
        collection = get_collection(Collections.TRANSACTIONS)
        query = {}
        
        if filters.get("is_fraud") is not None:
            query["is_fraud"] = filters["is_fraud"]
        
        if filters.get("risk_level"):
            query["risk_level"] = filters["risk_level"]
        
        if filters.get("min_amount"):
            query["transaction_amount"] = {"$gte": filters["min_amount"]}
        
        if filters.get("max_amount"):
            if "transaction_amount" in query:
                query["transaction_amount"]["$lte"] = filters["max_amount"]
            else:
                query["transaction_amount"] = {"$lte": filters["max_amount"]}
        
        if filters.get("transaction_type"):
            query["transaction_type"] = filters["transaction_type"]
        
        if filters.get("location"):
            query["location"] = filters["location"]
        
        if filters.get("start_date") and filters.get("end_date"):
            query["transaction_date"] = {
                "$gte": filters["start_date"],
                "$lte": filters["end_date"]
            }
        
        limit = filters.get("limit", 100)
        skip = filters.get("skip", 0)
        
        return list(collection.find(query)
                   .sort("created_at", pymongo.DESCENDING)
                   .skip(skip)
                   .limit(limit))
    
    @staticmethod
    def search_high_value_fraud(min_amount: float = 1000) -> List[Dict]:
        """Search for high-value fraudulent transactions"""
        collection = get_collection(Collections.TRANSACTIONS)
        return list(collection.find({
            "is_fraud": True,
            "transaction_amount": {"$gte": min_amount}
        }).sort("transaction_amount", pymongo.DESCENDING))
    
    @staticmethod
    def search_by_customer(customer_age: int = None, customer_occupation: str = None) -> List[Dict]:
        """Search transactions by customer details"""
        collection = get_collection(Collections.TRANSACTIONS)
        query = {}
        
        if customer_age:
            query["customer_age"] = customer_age
        
        if customer_occupation:
            query["customer_occupation"] = customer_occupation
        
        return list(collection.find(query).sort("created_at", pymongo.DESCENDING))

# ============================================================================
# DATA EXPORT UTILITIES
# ============================================================================

class DataExporter:
    """Export data in various formats"""
    
    @staticmethod
    def export_fraud_transactions_to_dict(start_date: str = None, end_date: str = None) -> List[Dict]:
        """Export fraud transactions as list of dictionaries"""
        if start_date and end_date:
            transactions = FraudTransaction.find_by_date_range(start_date, end_date)
        else:
            transactions = FraudTransaction.find_fraudulent(limit=1000)
        
        # Convert ObjectId to string for JSON serialization
        for t in transactions:
            if "_id" in t:
                t["_id"] = str(t["_id"])
        
        return transactions
    
    @staticmethod
    def export_alerts_to_dict(status: str = None) -> List[Dict]:
        """Export fraud alerts as list of dictionaries"""
        collection = get_collection(Collections.FRAUD_ALERTS)
        
        query = {}
        if status:
            query["status"] = status
        
        alerts = list(collection.find(query).sort("alert_date", pymongo.DESCENDING))
        
        # Convert ObjectId to string
        for a in alerts:
            if "_id" in a:
                a["_id"] = str(a["_id"])
            if "transaction_id" in a:
                a["transaction_id"] = str(a["transaction_id"])
        
        return alerts

# ============================================================================
# DATA CLEANUP UTILITIES
# ============================================================================

class DataCleanup:
    """Utilities for cleaning up old data"""
    
    @staticmethod
    def archive_old_transactions(days_old: int = 365):
        """Archive transactions older than specified days"""
        collection = get_collection(Collections.TRANSACTIONS)
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Count old transactions
        count = collection.count_documents({
            "created_at": {"$lt": cutoff_date}
        })
        
        print(f"Found {count} transactions older than {days_old} days")
        return count
    
    @staticmethod
    def delete_old_audit_logs(days_old: int = 90):
        """Delete audit logs older than specified days"""
        collection = get_collection(Collections.AUDIT_LOGS)
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        result = collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        print(f"Deleted {result.deleted_count} old audit log entries")
        return result.deleted_count

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class DataValidator:
    """Validate data integrity"""
    
    @staticmethod
    def validate_transaction_data(data: Dict) -> Tuple[bool, str]:
        """Validate transaction data before insertion"""
        required_fields = [
            "transaction_amount", "transaction_date", "transaction_type",
            "customer_age", "account_balance"
        ]
        
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate data types
        if not isinstance(data.get("transaction_amount"), (int, float)):
            return False, "transaction_amount must be a number"
        
        if not isinstance(data.get("customer_age"), int):
            return False, "customer_age must be an integer"
        
        # Validate ranges
        if data.get("transaction_amount", 0) < 0:
            return False, "transaction_amount cannot be negative"
        
        if not (0 <= data.get("customer_age", 0) <= 150):
            return False, "customer_age must be between 0 and 150"
        
        return True, "Valid"
    
    @staticmethod
    def check_database_integrity() -> Dict:
        """Check database integrity and return statistics"""
        stats = {
            "transactions_count": get_collection(Collections.TRANSACTIONS).count_documents({}),
            "fraud_alerts_count": get_collection(Collections.FRAUD_ALERTS).count_documents({}),
            "daily_stats_count": get_collection(Collections.DAILY_STATISTICS).count_documents({}),
            "audit_logs_count": get_collection(Collections.AUDIT_LOGS).count_documents({}),
            "model_performance_count": get_collection(Collections.MODEL_PERFORMANCE).count_documents({})
        }
        
        return stats

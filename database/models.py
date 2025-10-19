"""
Database Models/Schemas
Defines the structure and methods for each collection
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
import pymongo

from .config import get_collection, Collections

# ============================================================================
# FRAUD TRANSACTION MODEL
# ============================================================================

class FraudTransaction:
    """
    Model for storing fraud detection transaction results
    Collection: transactions
    """
    
    @staticmethod
    def create(transaction_data: Dict[str, Any], prediction_data: Dict[str, Any]) -> str:
        """
        Create a new transaction record
        
        Args:
            transaction_data: Original transaction data
            prediction_data: Model prediction results
            
        Returns:
            str: Inserted document ID
        """
        collection = get_collection(Collections.TRANSACTIONS)
        
        document = {
            # Transaction information
            "transaction_amount": transaction_data.get("TransactionAmount"),
            "transaction_date": transaction_data.get("TransactionDate"),
            "transaction_type": transaction_data.get("TransactionType"),
            "location": transaction_data.get("Location"),
            "channel": transaction_data.get("Channel"),
            
            # Customer information
            "customer_age": transaction_data.get("CustomerAge"),
            "customer_occupation": transaction_data.get("CustomerOccupation"),
            "account_balance": transaction_data.get("AccountBalance"),
            "account_status": transaction_data.get("Account Status"),
            
            # Transaction details
            "transaction_duration": transaction_data.get("TransactionDuration"),
            "login_attempts": transaction_data.get("LoginAttempts"),
            "previous_transaction_date": transaction_data.get("PreviousTransactionDate"),
            
            # Geographic information
            "sender_country": transaction_data.get("Sender Country"),
            "receiver_country": transaction_data.get("Receiver Country"),
            "sender_currency": transaction_data.get("Sender Currency"),
            "receiver_currency": transaction_data.get("Receiver Currency"),
            "is_cross_border": transaction_data.get("Sender Country") != transaction_data.get("Receiver Country"),
            
            # Security information
            "invalid_pin_status": transaction_data.get("Invalid Pin Status"),
            "invalid_pin_retry_limits": transaction_data.get("Invalid pin retry limits"),
            "invalid_pin_retry_count": transaction_data.get("Invalid pin retry count"),
            
            # Prediction results
            "is_fraud": prediction_data.get("is_fraud"),
            "fraud_probability": prediction_data.get("probability"),
            "risk_level": prediction_data.get("risk_level"),
            "confidence": prediction_data.get("confidence"),
            "action_recommended": prediction_data.get("action"),
            
            # Metadata
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "reviewed": False,
            "review_notes": None
        }
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(transaction_id: str) -> Optional[Dict]:
        """Find transaction by ID"""
        collection = get_collection(Collections.TRANSACTIONS)
        return collection.find_one({"_id": ObjectId(transaction_id)})
    
    @staticmethod
    def find_fraudulent(limit: int = 100, skip: int = 0) -> List[Dict]:
        """Find all fraudulent transactions"""
        collection = get_collection(Collections.TRANSACTIONS)
        return list(collection.find({"is_fraud": True})
                   .sort("created_at", pymongo.DESCENDING)
                   .skip(skip)
                   .limit(limit))

    @staticmethod
    def find_all(limit: int = 100, skip: int = 0) -> List[Dict]:
        """Find all transactions"""
        collection = get_collection(Collections.TRANSACTIONS)
        return list(collection.find()
                   .sort("created_at", pymongo.DESCENDING)
                   .skip(skip)
                   .limit(limit))

    @staticmethod
    def find_by_date_range(start_date: str, end_date: str) -> List[Dict]:
        """Find transactions within a date range"""
        collection = get_collection(Collections.TRANSACTIONS)
        return list(collection.find({
            "transaction_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("transaction_date", pymongo.DESCENDING))
    
    @staticmethod
    def find_by_risk_level(risk_level: str, limit: int = 100) -> List[Dict]:
        """Find transactions by risk level"""
        collection = get_collection(Collections.TRANSACTIONS)
        return list(collection.find({"risk_level": risk_level})
                   .sort("created_at", pymongo.DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def update_review_status(transaction_id: str, reviewed: bool, notes: str = None):
        """Update transaction review status"""
        collection = get_collection(Collections.TRANSACTIONS)
        return collection.update_one(
            {"_id": ObjectId(transaction_id)},
            {
                "$set": {
                    "reviewed": reviewed,
                    "review_notes": notes,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    def get_statistics(start_date: str = None, end_date: str = None) -> Dict:
        """Get transaction statistics"""
        collection = get_collection(Collections.TRANSACTIONS)
        
        query = {}
        if start_date and end_date:
            query["transaction_date"] = {"$gte": start_date, "$lte": end_date}
        
        total = collection.count_documents(query)
        fraud_count = collection.count_documents({**query, "is_fraud": True})
        
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$risk_level",
                    "count": {"$sum": 1}
                }
            }
        ]
        risk_distribution = list(collection.aggregate(pipeline))
        
        return {
            "total_transactions": total,
            "fraud_count": fraud_count,
            "legitimate_count": total - fraud_count,
            "fraud_percentage": (fraud_count / total * 100) if total > 0 else 0,
            "risk_distribution": risk_distribution
        }

# ============================================================================
# FRAUD ALERT MODEL
# ============================================================================

class FraudAlert:
    """
    Model for storing high-priority fraud alerts
    Collection: fraud_alerts
    """
    
    @staticmethod
    def create(transaction_id: str, alert_data: Dict[str, Any]) -> str:
        """Create a new fraud alert"""
        collection = get_collection(Collections.FRAUD_ALERTS)
        
        document = {
            "transaction_id": transaction_id,
            "alert_date": datetime.utcnow(),
            "severity": alert_data.get("severity", "high"),  # low, medium, high, critical
            "fraud_probability": alert_data.get("fraud_probability"),
            "risk_level": alert_data.get("risk_level"),
            "transaction_amount": alert_data.get("transaction_amount"),
            "customer_info": alert_data.get("customer_info"),
            "alert_reason": alert_data.get("alert_reason"),
            "recommended_action": alert_data.get("recommended_action"),
            "status": "pending",  # pending, investigating, resolved, false_positive
            "reviewed": False,
            "reviewed_by": None,
            "reviewed_at": None,
            "resolution_notes": None,
            "created_at": datetime.utcnow()
        }
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @staticmethod
    def find_pending_alerts(limit: int = 50) -> List[Dict]:
        """Find all pending fraud alerts"""
        collection = get_collection(Collections.FRAUD_ALERTS)
        return list(collection.find({"status": "pending"})
                   .sort("alert_date", pymongo.DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def update_alert_status(alert_id: str, status: str, reviewed_by: str = None, notes: str = None):
        """Update alert status"""
        collection = get_collection(Collections.FRAUD_ALERTS)
        return collection.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "status": status,
                    "reviewed": True,
                    "reviewed_by": reviewed_by,
                    "reviewed_at": datetime.utcnow(),
                    "resolution_notes": notes
                }
            }
        )
    
    @staticmethod
    def get_alert_statistics() -> Dict:
        """Get alert statistics"""
        collection = get_collection(Collections.FRAUD_ALERTS)
        
        total = collection.count_documents({})
        pending = collection.count_documents({"status": "pending"})
        resolved = collection.count_documents({"status": "resolved"})
        
        return {
            "total_alerts": total,
            "pending_alerts": pending,
            "resolved_alerts": resolved,
            "investigating": collection.count_documents({"status": "investigating"}),
            "false_positives": collection.count_documents({"status": "false_positive"})
        }

# ============================================================================
# MODEL PERFORMANCE MODEL
# ============================================================================

class ModelPerformance:
    """
    Model for tracking ML model performance metrics
    Collection: model_performance
    """
    
    @staticmethod
    def create(performance_data: Dict[str, Any]) -> str:
        """Create a new model performance record"""
        collection = get_collection(Collections.MODEL_PERFORMANCE)
        
        document = {
            "model_version": performance_data.get("model_version", "1.0"),
            "evaluation_date": datetime.utcnow(),
            "accuracy": performance_data.get("accuracy"),
            "precision": performance_data.get("precision"),
            "recall": performance_data.get("recall"),
            "f1_score": performance_data.get("f1_score"),
            "auc_roc": performance_data.get("auc_roc"),
            "confusion_matrix": performance_data.get("confusion_matrix"),
            "true_positives": performance_data.get("true_positives"),
            "true_negatives": performance_data.get("true_negatives"),
            "false_positives": performance_data.get("false_positives"),
            "false_negatives": performance_data.get("false_negatives"),
            "total_predictions": performance_data.get("total_predictions"),
            "notes": performance_data.get("notes"),
            "created_at": datetime.utcnow()
        }
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @staticmethod
    def get_latest_performance() -> Optional[Dict]:
        """Get the latest model performance metrics"""
        collection = get_collection(Collections.MODEL_PERFORMANCE)
        return collection.find_one(sort=[("evaluation_date", pymongo.DESCENDING)])
    
    @staticmethod
    def get_performance_history(limit: int = 10) -> List[Dict]:
        """Get model performance history"""
        collection = get_collection(Collections.MODEL_PERFORMANCE)
        return list(collection.find()
                   .sort("evaluation_date", pymongo.DESCENDING)
                   .limit(limit))

# ============================================================================
# DAILY STATISTICS MODEL
# ============================================================================

class DailyStatistics:
    """
    Model for storing daily aggregated statistics
    Collection: daily_statistics
    """
    
    @staticmethod
    def create_or_update(date: str, stats: Dict[str, Any]) -> str:
        """Create or update daily statistics"""
        collection = get_collection(Collections.DAILY_STATISTICS)
        
        document = {
            "date": date,
            "total_transactions": stats.get("total_transactions", 0),
            "fraud_detected": stats.get("fraud_detected", 0),
            "legitimate_transactions": stats.get("legitimate_transactions", 0),
            "fraud_percentage": stats.get("fraud_percentage", 0),
            "total_amount": stats.get("total_amount", 0),
            "fraud_amount": stats.get("fraud_amount", 0),
            "high_risk_transactions": stats.get("high_risk_transactions", 0),
            "medium_risk_transactions": stats.get("medium_risk_transactions", 0),
            "low_risk_transactions": stats.get("low_risk_transactions", 0),
            "alerts_generated": stats.get("alerts_generated", 0),
            "updated_at": datetime.utcnow()
        }
        
        result = collection.update_one(
            {"date": date},
            {"$set": document},
            upsert=True
        )
        
        return str(result.upserted_id) if result.upserted_id else "updated"
    
    @staticmethod
    def get_by_date(date: str) -> Optional[Dict]:
        """Get statistics for a specific date"""
        collection = get_collection(Collections.DAILY_STATISTICS)
        return collection.find_one({"date": date})
    
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[Dict]:
        """Get statistics for a date range"""
        collection = get_collection(Collections.DAILY_STATISTICS)
        return list(collection.find({
            "date": {"$gte": start_date, "$lte": end_date}
        }).sort("date", pymongo.ASCENDING))

# ============================================================================
# AUDIT LOG MODEL
# ============================================================================

class AuditLog:
    """
    Model for storing audit logs
    Collection: audit_logs
    """
    
    @staticmethod
    def create(log_data: Dict[str, Any]) -> str:
        """Create a new audit log entry"""
        collection = get_collection(Collections.AUDIT_LOGS)
        
        document = {
            "timestamp": datetime.utcnow(),
            "action_type": log_data.get("action_type"),  # create, update, delete, review, etc.
            "user_id": log_data.get("user_id"),
            "user_name": log_data.get("user_name"),
            "target_collection": log_data.get("target_collection"),
            "target_id": log_data.get("target_id"),
            "action_details": log_data.get("action_details"),
            "ip_address": log_data.get("ip_address"),
            "user_agent": log_data.get("user_agent")
        }
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @staticmethod
    def get_recent_logs(limit: int = 100) -> List[Dict]:
        """Get recent audit logs"""
        collection = get_collection(Collections.AUDIT_LOGS)
        return list(collection.find()
                   .sort("timestamp", pymongo.DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> List[Dict]:
        """Get audit logs for a specific user"""
        collection = get_collection(Collections.AUDIT_LOGS)
        return list(collection.find({"user_id": user_id})
                   .sort("timestamp", pymongo.DESCENDING)
                   .limit(limit))

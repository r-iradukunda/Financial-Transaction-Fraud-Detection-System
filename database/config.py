"""
MongoDB Database Configuration
Handles connection to MongoDB and provides database access
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        # MongoDB connection string - can be set via environment variable
        self.MONGO_URI = os.getenv(
            'MONGODB_URI',
            'mongodb://localhost:27017/'  # Default local MongoDB
        )
        
        # Database name
        self.DB_NAME = os.getenv('DB_NAME', 'fraud_detection_db')
        
        # Connection timeout
        self.TIMEOUT = 5000  # 5 seconds
        
        # MongoDB client
        self._client: Optional[MongoClient] = None
        self._db = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self._client = MongoClient(
                self.MONGO_URI,
                serverSelectionTimeoutMS=self.TIMEOUT
            )
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get database
            self._db = self._client[self.DB_NAME]
            
            print(f"✓ Connected to MongoDB database: {self.DB_NAME}")
            
            # Create indexes
            self._create_indexes()
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to MongoDB: {e}")
            return False
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Transactions collection indexes
            self._db.transactions.create_index([("transaction_date", DESCENDING)])
            self._db.transactions.create_index([("is_fraud", ASCENDING)])
            self._db.transactions.create_index([("customer_age", ASCENDING)])
            self._db.transactions.create_index([("transaction_type", ASCENDING)])
            self._db.transactions.create_index([("risk_level", ASCENDING)])
            self._db.transactions.create_index([("created_at", DESCENDING)])
            
            # Fraud alerts collection indexes
            self._db.fraud_alerts.create_index([("alert_date", DESCENDING)])
            self._db.fraud_alerts.create_index([("status", ASCENDING)])
            self._db.fraud_alerts.create_index([("severity", ASCENDING)])
            self._db.fraud_alerts.create_index([("reviewed", ASCENDING)])
            
            # Model performance collection indexes
            self._db.model_performance.create_index([("evaluation_date", DESCENDING)])
            self._db.model_performance.create_index([("model_version", ASCENDING)])
            
            # Daily statistics collection indexes
            self._db.daily_statistics.create_index([("date", DESCENDING)], unique=True)
            
            # Audit logs collection indexes
            self._db.audit_logs.create_index([("timestamp", DESCENDING)])
            self._db.audit_logs.create_index([("action_type", ASCENDING)])
            self._db.audit_logs.create_index([("user_id", ASCENDING)])
            
            print("✓ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠ Warning: Could not create indexes: {e}")
    
    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            print("✓ MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        db = self.get_database()
        return db[collection_name] if db is not None else None
    
    def drop_database(self):
        """Drop the entire database (USE WITH CAUTION!)"""
        if self._client:
            self._client.drop_database(self.DB_NAME)
            print(f"⚠ Database '{self.DB_NAME}' dropped")

# ============================================================================
# GLOBAL DATABASE INSTANCE
# ============================================================================

_db_config = DatabaseConfig()

def get_database():
    """Get database instance (singleton pattern)"""
    return _db_config.get_database()

def get_collection(collection_name: str):
    """Get a specific collection"""
    return _db_config.get_collection(collection_name)

def close_database():
    """Close database connection"""
    _db_config.close()

def initialize_database():
    """Initialize database connection"""
    return _db_config.connect()

# ============================================================================
# COLLECTION NAMES
# ============================================================================

class Collections:
    """Collection names constants"""
    TRANSACTIONS = "transactions"
    FRAUD_ALERTS = "fraud_alerts"
    MODEL_PERFORMANCE = "model_performance"
    DAILY_STATISTICS = "daily_statistics"
    AUDIT_LOGS = "audit_logs"
    USERS = "users"
    REPORTS = "reports"

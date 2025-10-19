"""
Test Database Connection
Simple script to test if MongoDB connection works
"""

print("="*70)
print("TESTING DATABASE CONNECTION")
print("="*70)

# Test 1: Check if pymongo is installed
print("\n1. Checking pymongo installation...")
try:
    import pymongo
    print(f"   ✓ pymongo {pymongo.__version__} installed")
except ImportError:
    print("   ✗ pymongo not installed")
    print("   Run: pip install pymongo")
    exit(1)

# Test 2: Check if python-dotenv is installed
print("\n2. Checking python-dotenv installation...")
try:
    import dotenv
    print(f"   ✓ python-dotenv installed")
except ImportError:
    print("   ✗ python-dotenv not installed")
    print("   Run: pip install python-dotenv")
    exit(1)

# Test 3: Try to connect to MongoDB
print("\n3. Testing MongoDB connection...")
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'fraud_detection_db')

print(f"   Connection URI: {MONGO_URI[:20]}...")
print(f"   Database name: {DB_NAME}")

try:
    from pymongo import MongoClient
    
    # Try to connect with 5 second timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    
    print("   ✓ Successfully connected to MongoDB!")
    
    # Get database
    db = client[DB_NAME]
    
    # List collections
    collections = db.list_collection_names()
    print(f"   ✓ Database '{DB_NAME}' accessible")
    print(f"   Collections: {collections if collections else 'None (new database)'}")
    
    # Close connection
    client.close()
    
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED - Ready to proceed!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run: python setup_database.py")
    print("2. Run: python app_with_database.py")
    print("="*70)
    
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    print("\n" + "="*70)
    print("CONNECTION FAILED - TROUBLESHOOTING")
    print("="*70)
    print("\nPossible solutions:")
    print("\n1. LOCAL MONGODB:")
    print("   - Make sure MongoDB is installed and running")
    print("   - Windows: Check Services for 'MongoDB Server'")
    print("   - Mac/Linux: Run 'sudo systemctl status mongod'")
    print("   - Start MongoDB: 'sudo systemctl start mongod'")
    print("\n2. MONGODB ATLAS (Cloud):")
    print("   - Create account at: https://www.mongodb.com/cloud/atlas")
    print("   - Create a free cluster (M0)")
    print("   - Whitelist IP: 0.0.0.0/0")
    print("   - Get connection string and add to .env file")
    print("\n3. CHECK .env FILE:")
    print("   - Make sure .env file exists in project root")
    print("   - Format: MONGODB_URI=mongodb://localhost:27017/")
    print("   - Format: DB_NAME=fraud_detection_db")
    print("\n" + "="*70)
    exit(1)

#!/usr/bin/env python3
"""
Quick Start Guide for Fraud Detection Test Client
Run this script to get started with testing
"""

import os
import sys
import subprocess
import webbrowser
import time

def print_header():
    """Print a nice header"""
    print("\n" + "="*70)
    print("  🔒 FRAUD DETECTION TEST CLIENT - QUICK START")
    print("="*70 + "\n")

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        'fraud_detection_model_decision_tree.joblib',
        'scaler.joblib',
        'label_encoders.joblib',
        'app.py',
        'static/index.html'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing.append(file)
    
    print()
    return len(missing) == 0

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Flask server...\n")
    
    try:
        # Start the app
        subprocess.Popen([sys.executable, 'app.py'])
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        print("✓ Server started!\n")
        return True
    except Exception as e:
        print(f"✗ Failed to start server: {e}\n")
        return False

def open_browser():
    """Open the test client in browser"""
    print("🌐 Opening test client in browser...\n")
    
    try:
        webbrowser.open('http://localhost:5000')
        print("✓ Browser opened!\n")
        return True
    except Exception as e:
        print(f"⚠ Could not open browser automatically: {e}")
        print("   Please manually visit: http://localhost:5000\n")
        return False

def print_instructions():
    """Print usage instructions"""
    print("="*70)
    print("📋 HOW TO USE\n")
    
    print("1. LOAD A TEMPLATE (Optional)")
    print("   - Click 'Legitimate' for a safe transaction")
    print("   - Click 'Suspicious' for a risky transaction\n")
    
    print("2. ENTER TRANSACTION DATA")
    print("   - Fill in the form with transaction details")
    print("   - All fields are validated\n")
    
    print("3. PREDICT FRAUD RISK")
    print("   - Click 'Predict Fraud Risk' button")
    print("   - Wait for real-time analysis\n")
    
    print("4. VIEW RESULTS")
    print("   - See fraud prediction: Legitimate or Fraud Detected")
    print("   - Risk level: Low (🟢) / Medium (🟡) / High (🔴)")
    print("   - Action: ALLOW / REVIEW / BLOCK\n")
    
    print("="*70 + "\n")

def print_examples():
    """Print example transactions"""
    print("💡 EXAMPLE TRANSACTIONS\n")
    
    print("LEGITIMATE TRANSACTION:")
    print("  • Amount: $150")
    print("  • Type: Withdrawal at ATM")
    print("  • Location: New York")
    print("  • Time: 14:30 (afternoon)")
    print("  • Account: Active, Valid PIN")
    print("  → Result: ✓ LEGITIMATE (ALLOW)\n")
    
    print("SUSPICIOUS TRANSACTION:")
    print("  • Amount: $5,000")
    print("  • Type: Online transfer")
    print("  • Location: Chicago (different from last transaction)")
    print("  • Time: 23:45 (late night)")
    print("  • Account: Flagged, Locked PIN")
    print("  • Cross-border: USA → Germany")
    print("  → Result: ⚠️ FRAUD DETECTED (BLOCK/REVIEW)\n")

def print_endpoints():
    """Print available API endpoints"""
    print("🔌 API ENDPOINTS\n")
    
    print("UI:")
    print("  • GET / → Test client interface\n")
    
    print("API Info:")
    print("  • GET /api → API overview")
    print("  • GET /api/health → Health check")
    print("  • GET /api/model-info → Model information\n")
    
    print("Predictions:")
    print("  • POST /api/predict → Single transaction")
    print("  • POST /api/predict/batch → Multiple transactions\n")

def main():
    """Main execution"""
    print_header()
    
    # Check files
    if not check_files():
        print("⚠ Some required files are missing!")
        print("Please ensure you have all model files in the project directory.\n")
        return False
    
    print_instructions()
    print_examples()
    print_endpoints()
    
    print("="*70)
    print("✅ EVERYTHING IS READY!\n")
    print("Server: http://localhost:5000")
    print("API:    http://localhost:5000/api")
    print("\n" + "="*70 + "\n")
    
    # Ask user if they want to start
    response = input("Start the server? (y/n): ").lower().strip()
    
    if response == 'y':
        if start_server():
            open_browser()
            print("🎉 Happy testing! Press Ctrl+C to stop the server.\n")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n✓ Server stopped. Goodbye! 👋\n")
        else:
            print("Failed to start server. Please run 'python app.py' manually.\n")
    else:
        print("\nTo start manually, run:")
        print("  python app.py\n")
        print("Then visit: http://localhost:5000\n")

if __name__ == '__main__':
    main()

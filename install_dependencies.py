"""
Installation Script
Installs all required dependencies for the fraud detection system with database
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print("="*70)
    print("FRAUD DETECTION SYSTEM - DEPENDENCY INSTALLATION")
    print("="*70)
    
    # List of packages to install
    packages = [
        ("pymongo>=4.5.0", "MongoDB Python Driver"),
        ("python-dotenv>=1.0.0", "Environment Variable Manager"),
        ("Flask==3.0.0", "Web Framework"),
        ("flask-cors==4.0.0", "CORS Support"),
        ("pandas==2.2.0", "Data Processing"),
        ("numpy==1.26.3", "Numerical Computing"),
        ("scikit-learn==1.3.2", "Machine Learning"),
    ]
    
    print("\nThe following packages will be installed:")
    for package, desc in packages:
        print(f"  - {package}: {desc}")
    
    print("\n" + "="*70)
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Upgrade pip first
    print("\n" + "="*70)
    print("Upgrading pip...")
    print("="*70)
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages
    success_count = 0
    failed_packages = []
    
    for package, desc in packages:
        if run_command(f"{sys.executable} -m pip install {package}", f"Installing {desc}"):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # Summary
    print("\n" + "="*70)
    print("INSTALLATION SUMMARY")
    print("="*70)
    print(f"Successfully installed: {success_count}/{len(packages)} packages")
    
    if failed_packages:
        print(f"\nFailed packages:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nTry installing failed packages manually:")
        print(f"pip install {' '.join(failed_packages)}")
    else:
        print("\n✓ All packages installed successfully!")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Install and start MongoDB:")
    print("   - Download: https://www.mongodb.com/try/download/community")
    print("   - OR use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas")
    print("\n2. Test database connection:")
    print("   python test_connection.py")
    print("\n3. Setup database with sample data:")
    print("   python setup_database.py")
    print("\n4. Run the API:")
    print("   python app_with_database.py")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)

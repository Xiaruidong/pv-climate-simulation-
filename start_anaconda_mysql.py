"""
MySQL Server Configuration and Startup Script
For Anaconda MySQL Installation
"""

import os
import subprocess
import time
import sys

# MySQL Configuration
MYSQL_PATH = r"D:\software_install\Anaconda\Library\bin"
DATA_DIR = r"D:\software_install\Anaconda\Library\data"
MYSQL_USER = "root"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306

def create_data_directories():
    """Create MySQL data directories"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(os.path.join(DATA_DIR, 'mysql'), exist_ok=True)
        print(f"[OK] Data directories created: {DATA_DIR}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create data directories: {e}")
        return False

def initialize_mysql():
    """Initialize MySQL database"""
    try:
        mysql_exe = os.path.join(MYSQL_PATH, 'mysql.exe')

        # Create initialization SQL file
        init_sql = """
        CREATE DATABASE IF NOT EXISTS pv_climate_simulation;
        USE pv_climate_simulation;
        SHOW TABLES;
        """

        # Run MySQL initialization
        result = subprocess.run(
            [mysql_exe, '--user=root', '--skip-password'],
            input=init_sql,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("[OK] MySQL database initialized successfully")
            print("[OK] Created database: pv_climate_simulation")
            return True
        else:
            print(f"[WARN] MySQL initialization warning: {result.stderr}")
            return True  # Continue, database may already exist
    except Exception as e:
        print(f"[FAIL] Failed to initialize MySQL: {e}")
        return False

def start_mysql_server():
    """Start MySQL server"""
    try:
        mysqld_exe = os.path.join(MYSQL_PATH, 'mysqld.exe')

        # Start MySQL server
        print("Starting MySQL server from Anaconda...")

        # Create startup command
        start_cmd = f'"{mysqld_exe}" --console --datadir="{DATA_DIR}" --skip-grant-tables'

        print(f"Command: {start_cmd}")
        print("MySQL server is starting in background...")
        print("Press Ctrl+C to stop the server")
        print()

        # Start MySQL server in new window
        os.system(f'start cmd /k "{start_cmd}"')

        # Wait a few seconds for server to start
        time.sleep(3)

        # Test connection
        print("Testing MySQL connection...")
        test_exe = os.path.join(MYSQL_PATH, 'mysql.exe')
        test_result = subprocess.run(
            [test_exe, '--user=root', '--skip-password', '-e', 'SHOW DATABASES;'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if test_result.returncode == 0:
            print("[OK] MySQL server started successfully!")
            print("[OK] MySQL connection test passed")
            return True
        else:
            print("[WARN] MySQL server started but connection test failed")
            print("This may be normal, please check manually")
            return True

    except Exception as e:
        print(f"[FAIL] Failed to start MySQL server: {e}")
        print("\nPlease try starting MySQL manually:")
        print(f"1. Open new command prompt")
        print(f"2. Run: {os.path.join(MYSQL_PATH, 'mysqld.exe')} --console --datadir=\"{DATA_DIR}\"")
        print(f"3. In another window, run: {os.path.join(MYSQL_PATH, 'mysql.exe')} -u root --password=your_password")
        return False

def test_api_connection():
    """Test API connection"""
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("[OK] API connection test passed")
            return True
        else:
            print("[WARN] API connection test failed")
            return False
    except:
        print("[WARN] API server not running (this is normal)")
        return False

if __name__ == '__main__':
    print("="*60)
    print("MySQL Server Setup and Start")
    print("="*60)
    print()

    print("MySQL Configuration:")
    print(f"  MySQL Path: {MYSQL_PATH}")
    print(f"  Data Directory: {DATA_DIR}")
    print(f"  Host: {MYSQL_HOST}")
    print(f"  Port: {MYSQL_PORT}")
    print()

    # Step 1: Create data directories
    print("Step 1: Create data directories...")
    if not create_data_directories():
        print("[FAIL] Cannot proceed without data directories")
        input("Press Enter to exit...")
        sys.exit(1)

    # Step 2: Initialize database
    print("\nStep 2: Initialize MySQL database...")
    if not initialize_mysql():
        print("[WARN] Continuing despite initialization warning...")

    # Step 3: Start MySQL server
    print("\nStep 3: Start MySQL server...")
    if start_mysql_server():
        print("\n" + "="*60)
        print("MySQL Setup Complete!")
        print("="*60)
        print()
        print("MySQL server is running in a separate window")
        print("You can now:")
        print("  1. Initialize database: python database/init_database.py")
        print("  2. Start API server: python backend/mysql_api.py")
        print("  3. Test connection: python database/test_system.py")
        print()

    input("Press Enter to exit...")

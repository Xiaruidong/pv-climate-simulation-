import os
import subprocess
import sys
import glob

def find_mysql_installation():
    """查找MySQL安装位置"""
    possible_paths = [
        r"C:\Program Files\MySQL",
        r"C:\Program Files (x86)\MySQL",
        r"D:\Program Files\MySQL",
        r"C:\xampp\mysql",
        r"C:\wamp64\bin\mysql.exe",
        r"C:\wamp\bin\mysql.exe",
        r"D:\software_install\Anaconda\Library\bin"
    ]

    found_paths = []

    for path in possible_paths:
        if os.path.exists(path):
            # 查找MySQL可执行文件
            if os.path.isfile(path):
                found_paths.append(path)
            else:
                # 搜索目录中的MySQL文件
                mysql_files = glob.glob(os.path.join(path, "**/mysql.exe"), recursive=True)
                mysqld_files = glob.glob(os.path.join(path, "**/mysqld.exe"), recursive=True)

                if mysql_files:
                    found_paths.extend(mysql_files)
                if mysqld_files:
                    found_paths.extend(mysqld_files)

    return found_paths

def check_mysql_service():
    """检查MySQL服务状态"""
    try:
        # 检查MySQL80服务
        result = subprocess.run(['sc', 'query', 'MySQL80'],
                              capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            return "MySQL80", "running"

        # 检查MySQL57服务
        result = subprocess.run(['sc', 'query', 'MySQL57'],
                              capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            return "MySQL57", "running"

        return None, "not_found"
    except Exception as e:
        return None, str(e)

def start_mysql_service():
    """启动MySQL服务"""
    try:
        # 尝试启动MySQL80
        result = subprocess.run(['net', 'start', 'MySQL80'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return "MySQL80", "started"

        # 尝试启动MySQL57
        result = subprocess.run(['net', 'start', 'MySQL57'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return "MySQL57", "started"

        return None, "failed"
    except Exception as e:
        return None, str(e)

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        # 尝试连接MySQL（无密码）
        result = subprocess.run(['mysql', '-u', 'root', '-p'],
                              capture_output=True, text=True,
                              input='\n')  # 输入空密码
        return "success"
    except:
        return "failed"

print("MySQL Installation Check")
print("=" * 50)
print()

# 查找MySQL安装
print("1. Searching for MySQL installation...")
mysql_paths = find_mysql_installation()

if mysql_paths:
    print("Found MySQL at:")
    for path in mysql_paths:
        print(f"  - {path}")
else:
    print("MySQL installation not found.")
    print("Please install MySQL from: https://dev.mysql.com/downloads/installer/")

print()

# 检查服务状态
print("2. Checking MySQL service status...")
service_name, service_status = check_mysql_service()

if service_name:
    print(f"Found service: {service_name}")
    print(f"Status: {service_status}")
else:
    print("MySQL service not found")

print()

# 如果服务存在但未运行，尝试启动
if service_name and service_status != "running":
    print("3. Attempting to start MySQL service...")
    service_name, start_result = start_mysql_service()

    if service_name:
        print(f"{service_name}: {start_result}")
    else:
        print("Failed to start service")
elif not service_name:
    print("No MySQL service found.")
    print("You may need to:")
    print("  - Install MySQL as Windows Service")
    print("  - Or run mysqld directly (see documentation)")

print()
print("=" * 50)
print("Recommendation:")
print("=" * 50)
print()

if mysql_paths:
    print("✅ MySQL is installed")
    if service_status == "running":
        print("✅ MySQL service is running")
        print()
        print("Next steps:")
        print("1. Update database password in backend/mysql_api.py")
        print("2. Run: python database/init_database.py")
        print("3. Start: python backend/mysql_api.py")
    else:
        print("⚠️ MySQL service is not running")
        print()
        print("Try one of these:")
        if "wamp" in str(mysql_paths).lower() or "xampp" in str(mysql_paths).lower():
            print("  - Start WAMP/XAMPP control panel")
            print("  - MySQL will start with the panel")
        else:
            print("  - Run: net start MySQL80")
            print("  - Or use MySQL Workbench to start server")
else:
    print("❌ MySQL not found")
    print()
    print("Please install MySQL first:")
    print("  1. Download: https://dev.mysql.com/downloads/installer/")
    print("  2. Or use XAMPP/WAMP which includes MySQL")

print()
input("Press Enter to exit...")

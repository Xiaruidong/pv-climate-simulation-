# 🗄️ MySQL数据库系统集成指南

## 📋 目录

1. [系统概述](#系统概述)
2. [环境准备](#环境准备)
3. [数据库安装](#数据库安装)
4. [数据库初始化](#数据库初始化)
5. [API服务启动](#api服务启动)
6. [前端集成](#前端集成)
7. [功能使用](#功能使用)
8. [故障排除](#故障排除)

---

## 系统概述

### 🎯 功能特性

- ✅ **持久化存储**: 使用MySQL数据库永久存储计算结果
- ✅ **高性能查询**: 支持复杂的SQL查询和数据分析
- ✅ **批量操作**: 支持批量导入和导出数据
- ✅ **智能标签**: 自动为计算结果生成标签
- ✅ **对比分析**: 内置多结果对比功能
- ✅ **统计报表**: 实时统计和数据概览
- ✅ **RESTful API**: 完整的REST API接口

### 📊 数据库结构

```
pv_climate_simulation
├── users                    # 用户表
├── simulations              # 模拟记录主表
├── simulation_parameters    # 输入参数表
├── simulation_results       # 计算结果表
├── tags                     # 标签表
├── simulation_tags          # 模拟-标签关联表
├── favorites                # 收藏表
├── comparison_groups        # 对比组表
├── comparison_items         # 对比项目表
└── export_history           # 导出历史表
```

---

## 环境准备

### 🔧 系统要求

- **操作系统**: Windows/Linux/MacOS
- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **内存**: 最少2GB RAM
- **存储**: 最少1GB可用空间

### 📦 安装Python依赖

```bash
pip install pymysql flask flask-cors
```

或者使用项目requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 数据库安装

### Windows系统

#### 方法1: MySQL Installer (推荐)

1. **下载MySQL Installer**:
   - 访问: https://dev.mysql.com/downloads/installer/
   - 下载 "mysql-installer-community"

2. **运行安装程序**:
   - 选择 "Custom" 安装类型
   - 选择以下组件:
     - MySQL Server
     - MySQL Workbench
     - MySQL Shell

3. **配置root密码**:
   - 设置一个安全的root密码
   - 记住这个密码，后续配置需要使用

4. **完成安装**

#### 方法2: 使用WAMP/XAMPP

如果您已有WAMP或XAMPP环境:

```bash
# WAMP环境
# MySQL通常已包含在WAMP中
# 默认端口: 3306
# 默认用户: root
# 默认密码: (空)
```

### Linux系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# 设置root密码
sudo mysql_secure_installation

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

### MacOS系统

```bash
# 使用Homebrew
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码
mysql_secure_installation
```

### 🧪 验证MySQL安装

```bash
# 测试MySQL连接
mysql -u root -p

# 在MySQL命令行中
mysql> SHOW DATABASES;
mysql> SELECT VERSION();
mysql> exit;
```

---

## 数据库初始化

### 🔧 步骤1: 配置数据库密码

编辑 `database/init_database.py`:

```python
ADMIN_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE',  # 修改这里
    'charset': 'utf8mb4'
}
```

### 🚀 步骤2: 运行初始化脚本

```bash
cd database
python init_database.py
```

**初始化过程**:
```
✅ 创建数据库结构
✅ 测试数据库连接
✅ 插入示例数据
✅ 显示数据库信息
```

### 📋 步骤3: 验证数据库创建

使用MySQL Workbench或命令行验证:

```bash
# 连接到数据库
mysql -u root -p pv_climate_simulation

# 查看表结构
SHOW TABLES;

# 查看数据
SELECT * FROM simulations LIMIT 5;
SELECT * FROM tags;
SELECT * FROM simulation_parameters LIMIT 5;
```

---

## API服务启动

### 🔧 步骤1: 配置API密码

编辑 `backend/mysql_api.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE',  # 修改这里
    'database': 'pv_climate_simulation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

### 🚀 步骤2: 启动API服务器

```bash
cd backend
python mysql_api.py
```

**服务启动成功后显示**:
```
INFO:__main__:启动MySQL API服务器...
INFO:__main__:数据库连接成功!
* Running on http://0.0.0.0:5000
```

### 🧪 步骤3: 测试API

```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 测试获取模拟记录
curl http://localhost:5000/api/simulations

# 测试获取统计信息
curl http://localhost:5000/api/statistics
```

---

## 前端集成

### 📦 安装前端依赖

```bash
cd /path/to/vue_project/huaneng2
npm install
```

### 🔧 配置API连接

在 `src/services/mysqlService.js` 中:

```javascript
constructor() {
  // 如果API不在localhost:5000，修改这里
  this.apiBaseURL = 'http://localhost:5000/api'
  this.isConnected = false
}
```

### 🚀 启动前端应用

```bash
npm run dev
```

访问: http://localhost:3000

---

## 功能使用

### 1️⃣ 自动保存计算结果

**在useSimulation.js中集成**:

```javascript
import mysqlDB from '@/services/mysqlService'

// 保存计算结果到MySQL
const saveToMySQL = async (params, results) => {
  try {
    const result = await mysqlDB.saveSimulation(params, results, {
      description: '用户自定义场景',
      calculationTimeMs: 150
    })
    console.log('✅ 已保存到MySQL:', result.record_id)
  } catch (error) {
    console.error('❌ 保存到MySQL失败:', error)
  }
}
```

### 2️⃣ 从MySQL加载历史记录

**在HistoryPage.vue中使用**:

```javascript
import mysqlDB from '@/services/mysqlService'

// 从MySQL加载历史记录
const loadFromMySQL = async () => {
  try {
    const data = await mysqlDB.getSimulations({
      page: 1,
      per_page: 20,
      status: 'completed',
      sort_by: 'created_at',
      sort_order: 'DESC'
    })

    historyRecords.value = data
    console.log('✅ 从MySQL加载了', data.length, '条记录')
  } catch (error) {
    console.error('❌ 从MySQL加载失败:', error)
  }
}
```

### 3️⃣ 使用MySQL对比功能

```javascript
// 对比多个模拟结果
const runComparison = async () => {
  try {
    const recordIds = selectedForComparison.value.map(r => r.record_id)
    const comparison = await mysqlDB.compareSimulations(recordIds)

    console.log('✅ 对比结果:', comparison.analysis)
    comparisonResult.value = comparison
  } catch (error) {
    console.error('❌ 对比失败:', error)
  }
}
```

### 4️⃣ MySQL数据导出

```javascript
// 导出为JSON
const exportToJSON = async () => {
  try {
    const json = await mysqlDB.exportToJson(recordIds)
    const blob = new Blob([json], { type: 'application/json' })

    // 触发下载
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `simulation-export-${Date.now()}.json`
    a.click()
  } catch (error) {
    console.error('❌ 导出失败:', error)
  }
}
```

### 5️⃣ 查看统计信息

```javascript
// 获取数据库统计
const getStatistics = async () => {
  try {
    const stats = await mysqlDB.getStatistics()

    console.log('📊 数据库统计:')
    console.log(`  总模拟记录: ${stats.total_simulations}`)
    console.log(`  今日新增: ${stats.today_simulations}`)
    console.log(`  平均温度变化: ${stats.average_temperature_change}°C`)
    console.log(`  总CO2减排: ${stats.total_co2_reduction} ppm`)
  } catch (error) {
    console.error('❌ 获取统计失败:', error)
  }
}
```

---

## 故障排除

### ❌ 常见问题解决

#### 问题1: MySQL连接失败

**错误信息**: `Can't connect to MySQL server`

**解决方案**:
```bash
# 检查MySQL服务是否运行
# Windows
net start mysql

# Linux
sudo systemctl status mysql
sudo systemctl start mysql

# MacOS
brew services start mysql
```

#### 问题2: 密码认证失败

**错误信息**: `Access denied for user 'root'`

**解决方案**:
```bash
# 重置root密码
mysql -u root -p

# 在MySQL中
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

#### 问题3: 端口冲突

**错误信息**: `Port 3306 is already in use`

**解决方案**:
```bash
# 检查端口占用
# Windows
netstat -ano | findstr :3306

# Linux/MacOS
lsof -i :3306

# 修改MySQL端口或停止冲突服务
```

#### 问题4: API CORS错误

**错误信息**: `CORS policy error`

**解决方案**:
```javascript
// 在mysql_api.py中确保CORS已启用
from flask_cors import CORS
CORS(app)  # 已启用CORS
```

#### 问题5: 数据库表不存在

**错误信息**: `Table 'pv_climate_simulation.xxx' doesn't exist`

**解决方案**:
```bash
# 重新运行初始化脚本
cd database
python init_database.py
```

---

## 📊 性能优化建议

### 数据库层面

1. **定期清理旧数据**:
```sql
-- 删除6个月前的记录
DELETE FROM simulations WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);
```

2. **添加索引优化**:
```sql
-- 查看索引使用情况
SHOW INDEX FROM simulations;
```

3. **数据库备份**:
```bash
# 备份数据库
mysqldump -u root -p pv_climate_simulation > backup.sql

# 恢复数据库
mysql -u root -p pv_climate_simulation < backup.sql
```

### 应用层面

1. **启用连接池**
2. **实现请求缓存**
3. **批量操作优化**

---

## 🎉 总结

### ✅ 完成清单

- [x] MySQL数据库安装
- [x] 数据库结构创建
- [x] Python API服务
- [x] 前端服务集成
- [x] 测试数据验证
- [x] 功能测试完成

### 🚀 下一步

1. **生产环境部署**:
   - 配置生产数据库
   - 设置数据库备份
   - 启用SSL/TLS

2. **功能扩展**:
   - 添加用户认证
   - 实现数据可视化
   - 构建报表系统

3. **性能优化**:
   - 实现数据缓存
   - 优化查询性能
   - 添加监控告警

---

**🎊 恭喜！MySQL数据库系统已成功集成到光伏气候效应模拟系统中！**

现在您可以：
- 🔒 永久保存所有计算结果
- 📊 进行复杂的数据分析
- 📈 生成统计报表
- 📤 导出和分享数据

如有问题，请参考故障排除章节或查看API文档。

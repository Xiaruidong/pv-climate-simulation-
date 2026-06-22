"""
MySQL数据库初始化脚本
用于创建数据库和表结构
"""

import pymysql
import logging
import os
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接配置（用于创建数据库）
ADMIN_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # 请修改为您的MySQL密码
    'charset': 'utf8mb4'
}

# 目标数据库配置
TARGET_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'pv_climate_simulation',
    'charset': 'utf8mb4'
}

def create_database():
    """创建数据库"""
    try:
        logger.info("正在创建数据库...")

        connection = pymysql.connect(**ADMIN_DB_CONFIG)
        cursor = connection.cursor()

        # 读取SQL文件
        schema_file = Path(__file__).parent / 'schema.sql'
        if not schema_file.exists():
            logger.error(f"找不到schema.sql文件: {schema_file}")
            return False

        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 分割SQL语句
        sql_statements = []
        current_statement = []

        for line in sql_content.split('\n'):
            # 跳过注释和空行
            if line.strip().startswith('--') or not line.strip():
                continue

            current_statement.append(line)

            # 检查语句结束
            if line.strip().endswith(';'):
                statement = ' '.join(current_statement)
                sql_statements.append(statement)
                current_statement = []

        # 执行SQL语句
        for statement in sql_statements:
            try:
                # 跳过DELIMITER语句
                if 'DELIMITER' in statement:
                    continue

                cursor.execute(statement)
                logger.info(f"✅ 执行成功: {statement[:50]}...")

            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"⚠️  警告: {e}")

        connection.commit()
        cursor.close()
        connection.close()

        logger.info("✅ 数据库创建完成!")
        return True

    except Exception as e:
        logger.error(f"❌ 创建数据库失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    try:
        logger.info("正在测试数据库连接...")

        connection = pymysql.connect(**TARGET_DB_CONFIG)
        cursor = connection.cursor()

        # 测试查询
        cursor.execute("SELECT COUNT(*) as count FROM simulations")
        result = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as count FROM tags")
        tags_count = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as count FROM simulation_results")
        results_count = cursor.fetchone()

        cursor.close()
        connection.close()

        logger.info("✅ 数据库连接测试成功!")
        logger.info(f"📊 当前数据:")
        logger.info(f"   - 模拟记录: {result['count']} 条")
        logger.info(f"   - 标签: {tags_count['count']} 个")
        logger.info(f"   - 计算结果: {results_count['count']} 条")

        return True

    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        return False

def insert_sample_data():
    """插入示例数据"""
    try:
        logger.info("正在插入示例数据...")

        connection = pymysql.connect(**TARGET_DB_CONFIG)
        cursor = connection.cursor()

        # 示例模拟数据
        sample_simulation = {
            'record_id': 'sample_001',
            'scenario_name': '示例场景 - 高覆盖率镜面面板',
            'description': '这是一个示例模拟记录，用于测试数据库功能',
            'status': 'completed',
            'calculation_time_ms': 150
        }

        # 插入模拟记录
        cursor.execute("""
            INSERT INTO simulations (record_id, scenario_name, description, status, calculation_time_ms)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            sample_simulation['record_id'],
            sample_simulation['scenario_name'],
            sample_simulation['description'],
            sample_simulation['status'],
            sample_simulation['calculation_time_ms']
        ))

        simulation_id = cursor.lastrowid

        # 插入参数
        cursor.execute("""
            INSERT INTO simulation_parameters
            (simulation_id, albedo_pv, coverage_ratio, pv_efficiency,
             albedo_land, albedo_ocean, co2_current, initial_temp,
             simulation_years, calculation_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            simulation_id,
            0.95,  # 镜面面板高反照率
            1e-7,  # 高覆盖率
            0.23,  # 标准光伏效率
            0.35,  # 沙漠陆地反照率
            0.06,  # 海洋反照率
            420.0,  # 当前CO2浓度
            15.0,  # 初始温度
            100,   # 模拟年数
            'euler' # 计算方法
        ))

        # 插入结果
        cursor.execute("""
            INSERT INTO simulation_results
            (simulation_id,
             baseline_equilibrium_temp, baseline_planetary_albedo,
             baseline_equilibrium_time, baseline_temperature_series, baseline_convergence,
             pv_equilibrium_temp, pv_planetary_albedo,
             pv_equilibrium_time, pv_co2_reduction, pv_final_co2_concentration,
             pv_temperature_series, pv_convergence,
             temperature_change, albedo_change, cooling_effect,
             heat_island_effect, cooling_efficiency, calculation_metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            simulation_id,
            15.0,  # 基准平衡温度
            0.300,  # 基准行星反照率
            50,    # 基准平衡时间
            json.dumps([15.0, 14.9, 14.8, 14.7, 14.6]),  # 温度序列
            json.dumps({'converged': True}),  # 收敛性
            12.5,  # 光伏平衡温度
            0.350,  # 光伏行星反照率
            45,    # 光伏平衡时间
            270.1234,  # CO2减排
            150.0,  # 最终CO2浓度
            json.dumps([15.0, 14.0, 13.5, 13.0, 12.5]),  # 温度序列
            json.dumps({'converged': True}),  # 收敛性
            -2.5,  # 温度变化
            0.05,  # 反照率变化
            True,  # 冷却效应
            -2.75, # 热岛效应
            25.0,  # 冷却效率
            json.dumps({'model': 'Real_EBM_v2.0', 'method': 'euler'})  # 元数据
        ))

        connection.commit()
        cursor.close()
        connection.close()

        logger.info("✅ 示例数据插入完成!")
        return True

    except Exception as e:
        logger.error(f"❌ 插入示例数据失败: {e}")
        return False

def show_database_info():
    """显示数据库信息"""
    try:
        logger.info("正在获取数据库信息...")

        connection = pymysql.connect(**TARGET_DB_CONFIG)
        cursor = connection.cursor()

        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        logger.info("📊 数据库表:")
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()
            logger.info(f"   - {table_name}: {count['count']} 条记录")

        # 获取标签
        cursor.execute("SELECT name, color FROM tags ORDER BY name")
        tags = cursor.fetchall()

        logger.info("🏷️  可用标签:")
        for tag in tags:
            logger.info(f"   - {tag['name']} (颜色: {tag['color']})")

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        logger.error(f"❌ 获取数据库信息失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 光伏气候效应模拟系统 - MySQL数据库初始化")
    print("=" * 60)

    # 检查密码配置
    if not ADMIN_DB_CONFIG['password']:
        print("⚠️  警告: MySQL密码未设置")
        print("请在此脚本中设置正确的MySQL密码:")
        print("ADMIN_DB_CONFIG['password'] = '您的密码'")
        print()

        # 提示用户输入密码
        password = input("请输入MySQL root密码 (按回车跳过): ").strip()
        if password:
            ADMIN_DB_CONFIG['password'] = password
            TARGET_DB_CONFIG['password'] = password
            print("✅ 密码已设置")
        else:
            print("⏭️  跳过密码设置")

    print()
    print("开始初始化流程...")
    print()

    # 执行初始化步骤
    steps = [
        ("创建数据库结构", create_database),
        ("测试数据库连接", test_database),
        ("插入示例数据", insert_sample_data),
        ("显示数据库信息", show_database_info)
    ]

    failed_steps = []

    for step_name, step_func in steps:
        print(f"📌 {step_name}...")
        if not step_func():
            failed_steps.append(step_name)
            print(f"❌ {step_name} 失败")
        else:
            print(f"✅ {step_name} 完成")
        print()

    # 显示结果
    print("=" * 60)
    if not failed_steps:
        print("🎉 数据库初始化完成!")
        print()
        print("📋 下一步操作:")
        print("1. 启动API服务器: python backend/mysql_api.py")
        print("2. 在浏览器中打开: http://localhost:5000/api/health")
        print("3. 查看API文档和测试接口")
    else:
        print("❌ 数据库初始化部分失败:")
        for step in failed_steps:
            print(f"   - {step}")
        print()
        print("请检查:")
        print("1. MySQL服务是否正在运行")
        print("2. 数据库配置是否正确")
        print("3. 是否有足够的权限")

    print("=" * 60)
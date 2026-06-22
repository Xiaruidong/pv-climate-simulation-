"""
MySQL数据库API服务
用于光伏气候效应模拟系统的数据存储
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pymysql
import pymysql.cursors
import json
import os
from datetime import datetime
from functools import wraps
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Anaconda MySQL uses empty password
    'database': 'pv_climate_simulation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'unix_socket': None,  # Using shared-memory connection for Anaconda MySQL
    'client_flag': 0  # Additional client flags if needed
}

# 数据库连接池
def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def execute_query(query, params=None, fetch_all=False):
    """执行SQL查询"""
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            connection.commit()
            return result
    except Exception as e:
        logger.error(f"查询执行失败: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

# ==================== 模拟记录相关API ====================

@app.route('/api/simulations', methods=['GET'])
def get_simulations():
    """获取模拟记录列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None)
        search = request.args.get('search', None)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'DESC')

        # 构建查询
        query = """
            SELECT SQL_CALC_FOUND_ROWS
            s.*, sp.*, sr.*,
            GROUP_CONCAT(DISTINCT t.name) as tags
            FROM simulations s
            LEFT JOIN simulation_parameters sp ON s.id = sp.simulation_id
            LEFT JOIN simulation_results sr ON s.id = sr.simulation_id
            LEFT JOIN simulation_tags st ON s.id = st.simulation_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE 1=1
        """
        params = []

        # 状态筛选
        if status:
            query += " AND s.status = %s"
            params.append(status)

        # 搜索筛选
        if search:
            query += " AND (s.scenario_name LIKE %s OR s.description LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])

        query += " GROUP BY s.id"

        # 排序
        valid_sort_fields = ['created_at', 'scenario_name', 'temperature_change', 'cooling_efficiency']
        if sort_by in valid_sort_fields:
            if sort_by == 'temperature_change':
                sort_by = 'sr.temperature_change'
            elif sort_by == 'cooling_efficiency':
                sort_by = 'sr.cooling_efficiency'
            else:
                sort_by = f's.{sort_by}'

            query += f" ORDER BY {sort_by} {sort_order}"

        # 分页
        offset = (page - 1) * per_page
        query += f" LIMIT {per_page} OFFSET {offset}"

        results = execute_query(query, params, fetch_all=True)

        # 获取总数
        count_result = execute_query("SELECT FOUND_ROWS() as total", fetch_all=False)
        total = count_result['total'] if count_result else 0

        return jsonify({
            'success': True,
            'data': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"获取模拟记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/simulations/<record_id>', methods=['GET'])
def get_simulation(record_id):
    """获取单个模拟记录详情"""
    try:
        query = """
            SELECT
                s.*,
                sp.*,
                sr.*,
                GROUP_CONCAT(DISTINCT t.name) as tags
            FROM simulations s
            LEFT JOIN simulation_parameters sp ON s.id = sp.simulation_id
            LEFT JOIN simulation_results sr ON s.id = sr.simulation_id
            LEFT JOIN simulation_tags st ON s.id = st.simulation_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE s.record_id = %s
            GROUP BY s.id
        """

        result = execute_query(query, (record_id,), fetch_all=False)

        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': '记录不存在'}), 404

    except Exception as e:
        logger.error(f"获取模拟记录详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/simulations', methods=['POST'])
def create_simulation():
    """创建新的模拟记录"""
    try:
        data = request.get_json()

        # 生成唯一记录ID
        record_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

        # 插入模拟记录
        sim_query = """
            INSERT INTO simulations (record_id, scenario_name, description, status, calculation_time_ms)
            VALUES (%s, %s, %s, %s, %s)
        """
        sim_params = (
            record_id,
            data.get('scenario_name', '未命名场景'),
            data.get('description'),
            'completed',
            data.get('calculation_time_ms')
        )

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 插入模拟记录
                cursor.execute(sim_query, sim_params)
                simulation_id = cursor.lastrowid

                # 插入参数
                params_query = """
                    INSERT INTO simulation_parameters
                    (simulation_id, albedo_pv, coverage_ratio, pv_efficiency,
                     albedo_land, albedo_ocean, co2_current, initial_temp,
                     simulation_years, calculation_method)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_values = (
                    simulation_id,
                    data['params'].get('albedo_pv', 0.438),
                    data['params'].get('coverage_ratio', 1e-8),
                    data['params'].get('pv_efficiency', 0.23),
                    data['params'].get('albedo_land', 0.35),
                    data['params'].get('albedo_ocean', 0.06),
                    data['params'].get('co2_current', 420.0),
                    data['params'].get('initial_temp', 15.0),
                    data['params'].get('simulation_years', 100),
                    data['params'].get('calculation_method', 'euler')
                )
                cursor.execute(params_query, params_values)

                # 插入结果
                if 'results' in data:
                    results = data['results']
                    results_query = """
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
                    """

                    baseline = results.get('baseline', {})
                    pv_scenario = results.get('pv_scenario', {})
                    comparison = results.get('comparison', {})

                    results_values = (
                        simulation_id,
                        baseline.get('equilibrium_temp', 0),
                        baseline.get('planetary_albedo', 0),
                        baseline.get('equilibrium_time', 0),
                        json.dumps(baseline.get('temperature_series', [])),
                        json.dumps(baseline.get('convergence', {})),
                        pv_scenario.get('equilibrium_temp', 0),
                        pv_scenario.get('planetary_albedo', 0),
                        pv_scenario.get('equilibrium_time', 0),
                        pv_scenario.get('co2_reduction', 0),
                        pv_scenario.get('final_co2_concentration', 420),
                        json.dumps(pv_scenario.get('temperature_series', [])),
                        json.dumps(pv_scenario.get('convergence', {})),
                        comparison.get('temperature_change', 0),
                        comparison.get('albedo_change', 0),
                        comparison.get('cooling_effect', False),
                        comparison.get('heat_island_effect', 0),
                        comparison.get('cooling_efficiency', 0),
                        json.dumps(results.get('metadata', {}))
                    )
                    cursor.execute(results_query, results_values)

                connection.commit()

                return jsonify({
                    'success': True,
                    'data': {'record_id': record_id, 'simulation_id': simulation_id}
                })

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    except Exception as e:
        logger.error(f"创建模拟记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/simulations/<record_id>', methods=['DELETE'])
def delete_simulation(record_id):
    """删除模拟记录"""
    try:
        query = "DELETE FROM simulations WHERE record_id = %s"
        execute_query(query, (record_id,))

        return jsonify({'success': True, 'message': '记录已删除'})

    except Exception as e:
        logger.error(f"删除模拟记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 对比功能API ====================

@app.route('/api/compare', methods=['POST'])
def compare_simulations():
    """对比多个模拟记录"""
    try:
        data = request.get_json()
        record_ids = data.get('record_ids', [])

        if len(record_ids) < 2:
            return jsonify({'success': False, 'error': '至少需要2条记录进行对比'}), 400

        # 构建查询
        placeholders = ','.join(['%s'] * len(record_ids))
        query = f"""
            SELECT
                s.id, s.record_id, s.scenario_name, s.created_at,
                sp.albedo_pv, sp.coverage_ratio, sp.pv_efficiency,
                sr.temperature_change, sr.pv_co2_reduction, sr.cooling_efficiency,
                sr.albedo_change
            FROM simulations s
            LEFT JOIN simulation_parameters sp ON s.id = sp.simulation_id
            LEFT JOIN simulation_results sr ON s.id = sr.simulation_id
            WHERE s.record_id IN ({placeholders})
        """

        results = execute_query(query, record_ids, fetch_all=True)

        # 分析对比结果
        if results:
            # 找出最佳结果
            best_cooling = min(results, key=lambda x: x['temperature_change'])
            best_co2 = max(results, key=lambda x: x['pv_co2_reduction'])
            best_efficiency = max(results, key=lambda x: x['cooling_efficiency'])

            analysis = {
                'best_cooling': best_cooling['record_id'],
                'best_co2_reduction': best_co2['record_id'],
                'best_efficiency': best_efficiency['record_id'],
                'total_records': len(results)
            }

            return jsonify({
                'success': True,
                'data': {
                    'results': results,
                    'analysis': analysis
                }
            })
        else:
            return jsonify({'success': False, 'error': '未找到相关记录'}), 404

    except Exception as e:
        logger.error(f"对比模拟记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 统计信息API ====================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        # 总记录数
        total_query = "SELECT COUNT(*) as total FROM simulations WHERE status = 'completed'"
        total_result = execute_query(total_query, fetch_all=False)
        total_count = total_result['total'] if total_result else 0

        # 今日新增
        today_query = """
            SELECT COUNT(*) as today_count
            FROM simulations
            WHERE DATE(created_at) = CURDATE() AND status = 'completed'
        """
        today_result = execute_query(today_query, fetch_all=False)
        today_count = today_result['today_count'] if today_result else 0

        # 平均温度变化
        temp_query = """
            SELECT AVG(temperature_change) as avg_temp_change
            FROM simulation_results
        """
        temp_result = execute_query(temp_query, fetch_all=False)
        avg_temp_change = temp_result['avg_temp_change'] if temp_result else 0

        # 总CO2减排
        co2_query = """
            SELECT SUM(pv_co2_reduction) as total_co2_reduction
            FROM simulation_results
        """
        co2_result = execute_query(co2_query, fetch_all=False)
        total_co2_reduction = co2_result['total_co2_reduction'] if co2_result else 0

        # 按状态统计
        status_query = """
            SELECT status, COUNT(*) as count
            FROM simulations
            GROUP BY status
        """
        status_results = execute_query(status_query, fetch_all=True)

        status_stats = {row['status']: row['count'] for row in status_results} if status_results else {}

        return jsonify({
            'success': True,
            'data': {
                'total_simulations': total_count,
                'today_simulations': today_count,
                'average_temperature_change': float(avg_temp_change) if avg_temp_change else 0,
                'total_co2_reduction': float(total_co2_reduction) if total_co2_reduction else 0,
                'status_statistics': status_stats
            }
        })

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 标签管理API ====================

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """获取所有标签"""
    try:
        query = "SELECT * FROM tags ORDER BY name"
        results = execute_query(query, fetch_all=True)

        return jsonify({'success': True, 'data': results})

    except Exception as e:
        logger.error(f"获取标签失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tags/<int:tag_id>/simulations', methods=['GET'])
def get_simulations_by_tag(tag_id):
    """获取特定标签的模拟记录"""
    try:
        query = """
            SELECT s.*, sp.*, sr.*
            FROM simulations s
            JOIN simulation_tags st ON s.id = st.simulation_id
            JOIN tags t ON st.tag_id = t.id
            LEFT JOIN simulation_parameters sp ON s.id = sp.simulation_id
            LEFT JOIN simulation_results sr ON s.id = sr.simulation_id
            WHERE t.id = %s AND s.status = 'completed'
            ORDER BY s.created_at DESC
        """

        results = execute_query(query, (tag_id,), fetch_all=True)

        return jsonify({'success': True, 'data': results})

    except Exception as e:
        logger.error(f"获取标签模拟记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 数据库健康检查API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """数据库健康检查"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            connection.close()

        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '资源不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500

# ==================== 启动服务器 ====================

if __name__ == '__main__':
    logger.info("启动MySQL API服务器...")

    # 测试数据库连接
    try:
        connection = get_db_connection()
        logger.info("数据库连接成功!")
        connection.close()
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        logger.error("请确保MySQL服务正在运行，并且数据库配置正确")

    # 启动Flask服务器
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
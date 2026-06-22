"""
MySQL数据库系统快速测试
用于验证数据库和API服务是否正常工作
"""

import requests
import json
import sys
from datetime import datetime

# API配置
API_BASE_URL = 'http://localhost:5000/api'

def print_section(title):
    """打印测试章节"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def test_api_connection():
    """测试API连接"""
    print_section("1️⃣ API连接测试")

    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        result = response.json()

        if result.get('success'):
            print("✅ API服务连接成功")
            print(f"   状态: {result.get('status')}")
            print(f"   数据库: {result.get('database')}")
            return True
        else:
            print("❌ API服务连接失败")
            print(f"   错误: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("   请确保API服务正在运行: python backend/mysql_api.py")
        return False

def create_test_simulation():
    """创建测试模拟记录"""
    print_section("2️⃣ 创建测试模拟记录")

    test_data = {
        'scenario_name': f'测试场景_{datetime.now().strftime("%H%M%S")}',
        'description': '这是自动化测试创建的模拟记录',
        'calculation_time_ms': 120,
        'params': {
            'albedo_pv': 0.95,
            'coverage_ratio': 1e-7,
            'pv_efficiency': 0.23,
            'albedo_land': 0.35,
            'albedo_ocean': 0.06,
            'co2_current': 420.0,
            'initial_temp': 15.0,
            'simulation_years': 100,
            'calculation_method': 'euler'
        },
        'results': {
            'baseline': {
                'equilibrium_temp': 15.0,
                'planetary_albedo': 0.300,
                'equilibrium_time': 50,
                'temperature_series': [15.0, 14.9, 14.8, 14.7, 14.6],
                'convergence': {'converged': True}
            },
            'pv_scenario': {
                'equilibrium_temp': 12.5,
                'planetary_albedo': 0.350,
                'equilibrium_time': 45,
                'co2_reduction': 270.1234,
                'final_co2_concentration': 150.0,
                'temperature_series': [15.0, 14.0, 13.5, 13.0, 12.5],
                'convergence': {'converged': True}
            },
            'comparison': {
                'temperature_change': -2.5,
                'albedo_change': 0.05,
                'cooling_effect': True,
                'heat_island_effect': -2.75,
                'cooling_efficiency': 25.0
            },
            'metadata': {
                'model': 'Real_EBM_v2.0',
                'method': 'euler'
            }
        }
    }

    try:
        response = requests.post(
            f'{API_BASE_URL}/simulations',
            json=test_data,
            timeout=10
        )
        result = response.json()

        if result.get('success'):
            print("✅ 测试模拟记录创建成功")
            print(f"   记录ID: {result['data']['record_id']}")
            return result['data']['record_id']
        else:
            print("❌ 创建模拟记录失败")
            print(f"   错误: {result.get('error')}")
            return None

    except Exception as e:
        print(f"❌ 创建模拟记录异常: {e}")
        return None

def test_get_simulations():
    """测试获取模拟记录"""
    print_section("3️⃣ 获取模拟记录测试")

    try:
        response = requests.get(f'{API_BASE_URL}/simulations', timeout=10)
        result = response.json()

        if result.get('success'):
            data = result.get('data', {})
            simulations = data if isinstance(data, list) else []
            pagination = result.get('pagination', {})

            print("✅ 获取模拟记录成功")
            print(f"   记录数量: {len(simulations)}")
            print(f"   当前页: {pagination.get('page', 1)}")
            print(f"   总页数: {pagination.get('pages', 1)}")

            if simulations:
                print(f"\n   最新记录:")
                for i, sim in enumerate(simulations[:3]):
                    print(f"   {i+1}. {sim.get('scenario_name', 'N/A')}")

            return len(simulations) > 0
        else:
            print("❌ 获取模拟记录失败")
            print(f"   错误: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 获取模拟记录异常: {e}")
        return False

def test_statistics():
    """测试统计信息"""
    print_section("4️⃣ 统计信息测试")

    try:
        response = requests.get(f'{API_BASE_URL}/statistics', timeout=10)
        result = response.json()

        if result.get('success'):
            stats = result['data']
            print("✅ 获取统计信息成功")
            print(f"   总模拟记录: {stats.get('total_simulations', 0)}")
            print(f"   今日新增: {stats.get('today_simulations', 0)}")
            print(f"   平均温度变化: {stats.get('average_temperature_change', 0):.4f}°C")
            print(f"   总CO2减排: {stats.get('total_co2_reduction', 0):.2f} ppm")
            print(f"   状态统计: {stats.get('status_statistics', {})}")
            return True
        else:
            print("❌ 获取统计信息失败")
            print(f"   错误: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 获取统计信息异常: {e}")
        return False

def test_comparison(record_id):
    """测试对比功能"""
    print_section("5️⃣ 对比功能测试")

    if not record_id:
        print("⏭️  跳过对比测试（无可用记录）")
        return True

    try:
        # 首先获取多个记录
        response = requests.get(f'{API_BASE_URL}/simulations', timeout=10)
        result = response.json()

        if result.get('success'):
            simulations = result.get('data', [])
            if isinstance(simulations, list) and len(simulations) >= 2:
                # 选择前2条记录进行对比
                record_ids = [sim['record_id'] for sim in simulations[:2]]

                response = requests.post(
                    f'{API_BASE_URL}/compare',
                    json={'record_ids': record_ids},
                    timeout=10
                )
                result = response.json()

                if result.get('success'):
                    comparison = result['data']
                    print("✅ 对比功能测试成功")
                    print(f"   对比记录数: {len(comparison['results'])}")
                    print(f"   最佳降温: {comparison['analysis'].get('best_cooling')}")
                    print(f"   最大CO2减排: {comparison['analysis'].get('best_co2_reduction')}")
                    print(f"   最高效率: {comparison['analysis'].get('best_efficiency')}")
                    return True
                else:
                    print("❌ 对比功能失败")
                    print(f"   错误: {result.get('error')}")
                    return False
            else:
                print("⏭️  跳过对比测试（记录数量不足）")
                return True
        else:
            print("❌ 获取对比记录失败")
            return False

    except Exception as e:
        print(f"❌ 对比功能异常: {e}")
        return False

def test_tags():
    """测试标签功能"""
    print_section("6️⃣ 标签功能测试")

    try:
        response = requests.get(f'{API_BASE_URL}/tags', timeout=10)
        result = response.json()

        if result.get('success'):
            tags = result['data']
            print("✅ 获取标签成功")
            print(f"   标签数量: {len(tags)}")

            if tags:
                print(f"\n   可用标签:")
                for i, tag in enumerate(tags[:5]):
                    print(f"   {i+1}. {tag['name']} (颜色: {tag['color']})")

            return True
        else:
            print("❌ 获取标签失败")
            print(f"   错误: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 标签功能异常: {e}")
        return False

def cleanup_test_data(record_id):
    """清理测试数据"""
    print_section("7️⃣ 清理测试数据")

    if not record_id:
        print("⏭️  无需清理")
        return

    try:
        response = requests.delete(f'{API_BASE_URL}/simulations/{record_id}', timeout=10)
        result = response.json()

        if result.get('success'):
            print("✅ 测试数据已清理")
        else:
            print("⚠️  清理测试数据失败（可能需要手动删除）")

    except Exception as e:
        print(f"⚠️  清理测试数据异常: {e}")

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 MySQL数据库系统 - 自动化测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE_URL}")

    # 运行测试
    results = []

    # 1. API连接测试
    if not test_api_connection():
        print("\n❌ API连接失败，请检查:")
        print("   1. API服务是否启动: python backend/mysql_api.py")
        print("   2. MySQL服务是否运行")
        print("   3. 数据库配置是否正确")
        return

    # 2. 创建测试记录
    record_id = create_test_simulation()
    if record_id:
        results.append(("创建测试记录", True))

    # 3. 获取模拟记录
    if test_get_simulations():
        results.append(("获取模拟记录", True))

    # 4. 统计信息
    if test_statistics():
        results.append(("统计信息", True))

    # 5. 对比功能
    if test_comparison(record_id):
        results.append(("对比功能", True))

    # 6. 标签功能
    if test_tags():
        results.append(("标签功能", True))

    # 7. 清理测试数据
    cleanup_test_data(record_id)

    # 显示测试结果
    print_section("📊 测试结果汇总")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！MySQL数据库系统工作正常！")
        print("\n📋 下一步:")
        print("   1. 在Vue应用中集成MySQL服务")
        print("   2. 测试历史记录功能")
        print("   3. 测试数据对比功能")
        print("   4. 测试数据导出功能")
    else:
        print("\n⚠️  部分测试失败，请检查相关功能")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
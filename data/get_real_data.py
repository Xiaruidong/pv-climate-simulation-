"""
快速环境数据获取脚本
一键获取各类环境数据并保存为标准格式
"""

import json
import requests
from datetime import datetime
import sys

def get_world_bank_carbon_data():
    """获取世界银行碳排放数据"""
    indicators = {
        'CO2_emissions': 'EN.ATM.CO2E.KT',  # CO2排放量(千吨)
        'CO2_per_capita': 'EN.ATM.CO2E.PC',  # 人均CO2排放(吨)
        'CO2_per_GDP': 'EN.ATM.CO2E.KD.GD',  # 单位GDP CO2排放(千克/美元)
        'renewable_energy': 'EG.FEC.RNEW.ZS',  # 可再生能源占比(%)
        'energy_consumption': 'EG.USE.COMM.KT.OE'  # 能源消耗(千吨油当量)
    }

    base_url = "http://api.worldbank.org/v2/country/CHN/indicator/"

    data = {}
    for name, indicator in indicators.items():
        try:
            url = f"{base_url}{indicator}?format=json&per_page=20"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()

            if len(result) > 1 and result[1]:
                data[name] = [
                    {
                        'year': item['date'],
                        'value': item['value']
                    }
                    for item in result[1] if item['value'] is not None
                ]
                print(f"✅ 获取 {name} 数据成功")
            else:
                print(f"⚠️  {name} 无数据")
                data[name] = []

        except Exception as e:
            print(f"❌ 获取 {name} 失败: {str(e)}")
            data[name] = []

    return data

def get_china_official_data():
    """获取中国官方数据链接"""
    sources = {
        '国家统计局': 'http://www.stats.gov.cn/sj/hj/',
        '生态环境部': 'https://www.mee.gov.cn/hjzl/',
        '国家能源局': 'http://www.nea.gov.cn/',
        '碳交易数据': 'https://www.cneeex.com/',
        'CEADs碳数据库': 'http://www.ceads.net.cn/'
    }
    return sources

def save_comprehensive_data():
    """保存综合环境数据"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 获取世界银行数据
    print("🌍 正在获取世界银行数据...")
    world_bank_data = get_world_bank_carbon_data()

    # 获取中国数据源
    print("🇨🇳 正在获取中国官方数据源...")
    china_sources = get_china_official_data()

    # 组合数据
    comprehensive_data = {
        'metadata': {
            'created_at': timestamp,
            'data_version': '1.0',
            'data_sources': [
                '世界银行开放数据',
                '中国官方统计数据',
                '示例数据补充'
            ],
            'note': '此数据包含API获取的实时数据和官方数据源链接'
        },
        'world_bank_data': world_bank_data,
        'china_official_sources': china_sources,
        'usage_guide': {
            'world_bank_data': '可直接使用API数据',
            'official_sources': '访问官方链接获取详细数据',
            'recommendations': '建议优先使用官方统计数据'
        }
    }

    # 保存数据
    filename = f'data/environmental_data_{datetime.now().strftime("%Y%m%d")}.json'
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
        print(f"📊 数据已保存到: {filename}")

        # 同时保存为固定文件名
        fixed_filename = 'data/current_environmental_data.json'
        with open(fixed_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
        print(f"📊 同时保存为: {fixed_filename}")

        return comprehensive_data
    except Exception as e:
        print(f"❌ 保存数据失败: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 开始获取环境数据...")
    print("-" * 50)

    try:
        data = save_comprehensive_data()

        if data:
            print("-" * 50)
            print("✅ 数据获取完成！")
            print("\n📋 数据摘要:")
            print(f"  - CO2排放数据: {len(data['world_bank_data'].get('CO2_emissions', []))} 年")
            print(f"  - 人均排放数据: {len(data['world_bank_data'].get('CO2_per_capita', []))} 年")
            print(f"  - 官方数据源: {len(data['china_official_sources'])} 个")
            print("\n💡 使用建议:")
            print("  1. 查看JSON文件了解数据结构")
            print("  2. 访问官方链接获取更详细数据")
            print("  3. 定期运行此脚本更新数据")
    except Exception as e:
        print(f"❌ 数据获取失败: {str(e)}")
        print("💡 建议: 检查网络连接或使用示例数据")

    print("\n按任意键退出...")
    input()

# -*- coding: utf-8 -*-
"""
环境数据获取工具 - 简化版本
避免编码问题，专注数据获取
"""

import json
import requests
from datetime import datetime
import sys
import os

def print_safe(text):
    """安全打印，避免编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

def get_world_bank_data():
    """获取世界银行环境数据"""
    print_safe("[INFO] 开始获取世界银行数据...")

    indicators = {
        'CO2_emissions': 'EN.ATM.CO2E.KT',
        'CO2_per_capita': 'EN.ATM.CO2E.PC',
        'CO2_per_GDP': 'EN.ATM.CO2E.KD.GD',
        'renewable_energy': 'EG.FEC.RNEW.ZS',
        'energy_consumption': 'EG.USE.COMM.KT.OE',
        'forest_area': 'AG.LND.FRST.K2',
        'electric_power_consumption': 'EG.USE.ELEC.KH.PC'
    }

    base_url = "http://api.worldbank.org/v2/country/CHN/indicator/"
    data = {}

    for name, indicator in indicators.items():
        try:
            url = f"{base_url}{indicator}?format=json&per_page=20"
            print_safe(f"[INFO] 获取 {name} 数据...")

            response = requests.get(url, timeout=15)
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
                print_safe(f"[SUCCESS] 获取 {name} 数据成功 - {len(data[name])} 年数据")
            else:
                print_safe(f"[WARNING] {name} 无数据")
                data[name] = []

        except Exception as e:
            print_safe(f"[ERROR] 获取 {name} 失败: {str(e)}")
            data[name] = []

    return data

def get_sample_data():
    """生成示例数据作为补充"""
    print_safe("[INFO] 生成示例补充数据...")

    sample_data = {
        'pollution_emissions': {
            'SO2': {'2020': 877.3, '2021': 756.2, '2022': 689.1},
            'NOx': {'2020': 1234.5, '2021': 1123.4, '2022': 1098.7},
            'PM25': {'2020': 567.8, '2021': 456.7, '2022': 398.5}
        },
        'light_pollution': {
            'urban_index': 3.8,
            'artificial_brightness': 125.4,
            'growth_rate': 3.2
        },
        'energy_saving': {
            'total_2022': 6890.1,
            'industrial': 3456.7,
            'building': 1234.5
        },
        'pv_specific': {
            'installed_capacity_2022': 392.6,  # GW
            'generation_2022': 456.7,  # TWh
            'carbon_reduction': 189.3  # Mt CO2
        }
    }

    print_safe("[SUCCESS] 示例数据生成完成")
    return sample_data

def save_all_data(world_bank_data, sample_data):
    """保存所有数据"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    comprehensive_data = {
        'metadata': {
            'created_at': timestamp,
            'version': '2.0',
            'data_sources': [
                'World Bank Open Data API',
                'China Official Statistics (sample)',
                'Research Data (sample)'
            ]
        },
        'world_bank_official': world_bank_data,
        'sample_supplementary': sample_data,
        'data_source_links': {
            'world_bank': 'https://data.worldbank.org/',
            'china_stats': 'http://www.stats.gov.cn/',
            'mee_env': 'https://www.mee.gov.cn/',
            'iea_stats': 'https://www.iea.org/data-and-statistics/',
            'ceads': 'http://www.ceads.net.cn/'
        },
        'usage_note': '世界银行数据为官方API获取，示例数据供开发参考'
    }

    # 确保data目录存在
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 保存当前数据
    current_file = os.path.join(data_dir, 'current_environmental_data.json')
    try:
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
        print_safe(f"[SUCCESS] 数据已保存: {current_file}")
    except Exception as e:
        print_safe(f"[ERROR] 保存数据失败: {str(e)}")
        return None

    # 保存带时间戳的数据
    timestamp_file = os.path.join(data_dir, f'environmental_data_{datetime.now().strftime("%Y%m%d_%H%M")}.json')
    try:
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
        print_safe(f"[SUCCESS] 历史数据已保存: {timestamp_file}")
    except Exception as e:
        print_safe(f"[WARNING] 历史数据保存失败: {str(e)}")

    return comprehensive_data

def main():
    """主函数"""
    print_safe("="*60)
    print_safe("Environmental Data Fetcher Tool v2.0")
    print_safe("="*60)

    try:
        # 获取世界银行数据
        print_safe("\n[STEP 1/3] 获取世界银行官方数据...")
        world_bank_data = get_world_bank_data()

        # 获取示例补充数据
        print_safe("\n[STEP 2/3] 生成示例补充数据...")
        sample_data = get_sample_data()

        # 保存数据
        print_safe("\n[STEP 3/3] 保存数据文件...")
        final_data = save_all_data(world_bank_data, sample_data)

        if final_data:
            print_safe("\n" + "="*60)
            print_safe("Data fetch completed successfully!")
            print_safe("="*60)
            print_safe("\nGenerated files:")
            print_safe("- data/current_environmental_data.json")
            print_safe("- data/environmental_data_YYYYMMDD_HHMM.json")

            print_safe("\nData summary:")
            for key, value in world_bank_data.items():
                if value:
                    print_safe(f"  - {key}: {len(value)} years of data")

            print_safe("\nOfficial data sources:")
            for source, url in final_data['data_source_links'].items():
                print_safe(f"  - {source}: {url}")

            print_safe("\nRecommendations:")
            print_safe("1. Check current_environmental_data.json for data structure")
            print_safe("2. Visit official links for more detailed data")
            print_safe("3. Run this script regularly to update data")

        else:
            print_safe("[ERROR] Data fetch failed")
            return 1

        return 0

    except Exception as e:
        print_safe(f"[FATAL ERROR] {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

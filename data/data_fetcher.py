"""
环境数据获取工具
支持从多个数据源获取环境、污染、碳排放等数据
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

class EnvironmentalDataFetcher:
    """环境数据获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Environmental Data Fetcher 1.0'
        })

    def fetch_world_bank_data(self, indicator, country='CHN', start_year=2020, end_year=2023):
        """
        获取世界银行环境数据

        Args:
            indicator: 指标代码 (如: EN.ATM.CO2E.KT for CO2 emissions)
            country: 国家代码 (默认中国)
            start_year: 开始年份
            end_year: 结束年份

        Returns:
            DataFrame: 数据表格
        """
        base_url = "http://api.worldbank.org/v2/country"

        try:
            url = f"{base_url}/{country}/indicator/{indicator}"
            params = {
                'format': 'json',
                'per_page': 1000,
                'date': f"{start_year}:{end_year}"
            }

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if len(data) > 1 and data[1]:
                df = pd.DataFrame(data[1])
                df = df[['date', 'value']].dropna()
                df.columns = ['year', 'value']
                df['year'] = df['year'].astype(int)
                df['value'] = df['value'].astype(float)
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            print(f"获取世界银行数据失败: {str(e)}")
            return pd.DataFrame()

    def fetch_iea_data(self, data_type='CO2'):
        """
        获取IEA能源数据

        Args:
            data_type: 数据类型 (CO2, Energy, Renewables)

        Returns:
            dict: 数据字典
        """
        # IEA数据通常需要API密钥，这里提供示例结构
        sample_data = {
            'data_type': data_type,
            'source': 'IEA Statistics',
            'note': 'IEA数据需要官方API访问权限'
        }
        return sample_data

    def fetch_china_stats(self):
        """
        获取中国官方统计数据

        Returns:
            dict: 中国环境统计数据
        """
        # 这里提供数据获取的框架和示例数据
        china_data = {
            'source': '国家统计局、生态环境部',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'data_categories': {
                'energy_consumption': '能源消费总量',
                'carbon_emissions': '二氧化碳排放量',
                'pollution_emissions': '主要污染物排放量',
                'industrial_output': '工业产值'
            },
            'access_methods': [
                '官方网站下载',
                'API接口',
                '统计年鉴',
                '数据公报'
            ]
        }
        return china_data

    def generate_sample_data(self):
        """
        生成示例环境数据

        Returns:
            dict: 完整的示例数据集
        """
        sample_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_type': 'sample_data_for_development',
                'note': '这是示例数据，实际使用请获取官方数据'
            },
            'energy_consumption': {
                'total': {
                    '2020': 49.8,  # 亿吨标准煤
                    '2021': 52.3,
                    '2022': 54.1
                },
                'coal_percentage': 56.2,
                'renewable_percentage': 15.3,
                'trend': 'slowly_increasing'
            },
            'carbon_emissions': {
                'total': {
                    '2020': 98.7,  # 亿吨CO2
                    '2021': 97.8,
                    '2022': 96.5
                },
                'per_capita': 6.8,  # 吨CO2/人
                'intensity': 0.56,  # 吨CO2/万元GDP
                'trend': 'slowly_decreasing'
            },
            'pollution_emissions': {
                'SO2': 689.1,  # 万吨
                'NOx': 1098.7,
                'PM10': 567.8,
                'PM2_5': 398.5,
                'trend': 'decreasing'
            },
            'light_pollution': {
                'urban_lighting_index': 3.8,
                'artificial_brightness': 125.4,
                'growth_rate': 3.2,  # 年增长率%
                'trend': 'increasing'
            },
            'energy_saving': {
                'total_saving': 6890.1,  # 万吨标准煤
                'industrial_saving': 3456.7,
                'building_saving': 1234.5,
                'transport_saving': 890.2,
                'household_saving': 1234.5
            }
        }
        return sample_data

    def save_data(self, data, filename='environmental_data.json'):
        """
        保存数据到JSON文件

        Args:
            data: 要保存的数据
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
        except Exception as e:
            print(f"保存数据失败: {str(e)}")

    def load_data(self, filename='environmental_data.json'):
        """
        从JSON文件加载数据

        Args:
            filename: 文件名

        Returns:
            dict: 加载的数据
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"数据已从 {filename} 加载")
            return data
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
            return None
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            return None


# 使用示例
if __name__ == "__main__":
    fetcher = EnvironmentalDataFetcher()

    # 生成示例数据
    print("生成示例环境数据...")
    sample_data = fetcher.generate_sample_data()

    # 保存数据
    fetcher.save_data(sample_data, 'data/sample_environmental_data.json')

    # 尝试获取世界银行数据
    print("\n尝试获取世界银行CO2排放数据...")
    wb_data = fetcher.fetch_world_bank_data('EN.ATM.CO2E.KT')
    if not wb_data.empty:
        print("世界银行数据获取成功:")
        print(wb_data)
    else:
        print("世界银行数据获取失败，使用示例数据")

    print("\n数据获取完成！")

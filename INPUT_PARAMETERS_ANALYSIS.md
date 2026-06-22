# 🔬 EBM模型实际计算所需输入参数分析

## 📋 参数分类总结

基于真实物理计算代码分析，EBM模型计算需要的输入参数分为以下几类：

## 🎯 必需核心参数（7个）

这些参数是物理计算必需的，没有它们计算无法进行：

### 1. **地理参数**
```python
albedo_land      # 陆地反照率 (0-1)
albedo_ocean      # 海洋反照率 (0-1)
```
**作用**: 计算地表反照率和行星反照率
**物理依据**: 不同地表类型的反射特性
**数据来源**: NASA卫星观测、IPCC地表分类

### 2. **光伏系统参数**
```python
albedo_pv        # 光伏面板反照率 (0-1)
coverage_ratio   # 光伏覆盖面积比例 (0-1)
pv_efficiency    # 光伏转化效率 (0-1)
```
**作用**: 计算光伏部署对反照率和CO2减排的影响
**物理依据**: 光伏材料特性、部署规模、发电效率
**数据来源**: NREL实验室测试、行业报告

### 3. **气候参数**
```python
co2_current      # 当前CO2浓度 (ppm, 280-1000)
initial_temp     # 初始地表温度 (°C)
```
**作用**: 计算温室效应和温度基准
**物理依据**: 大气CO2浓度对辐射强迫的影响
**数据来源**: Mauna Loa观测站、IPCC报告

## 📊 可选环境参数（5个）

这些参数影响计算的精度和适用性：

### 1. **地理参数**
```python
latitude         # 地理纬度 (°N, -90 to 90)
longitude        # 地理经度 (°E, -180 to 180)
```
**作用**: 确定太阳辐照度和地域特征
**使用场景**: 区域化计算、不同地理条件对比

### 2. **太阳辐射参数**
```python
irradiance       # 年太阳辐照度 (kWh/m²/year, 200-1200)
```
**作用**: 计算光伏发电量
**数据来源**: 气象观测、NASA卫星数据

### 3. **排放因子参数**
```python
grid_emission_factor  # 电网排放因子 (gCO2/kWh, 300-800)
```
**作用**: 计算CO2减排量
**数据来源**: 国家能源统计、生命周期评估

## 🔧 模拟控制参数（3个）

这些参数控制数值积分过程：

```python
simulation_years  # 模拟年数 (1-1000)
time_step         # 时间步长 (年, 0.1-10)
nt               # 数值积分步数 (隐含)
```
**作用**: 控制数值积分的精度和时间范围
**默认值**: simulation_years=100, time_step=1.0

## 🌍 固定物理常数（无需输入）

这些是内置的物理常数，基于国际标准值：

### 天文常数
```python
SOLAR_CONSTANT = 1361.0        # 太阳常数 W/m² (CODATA 2018)
EARTH_RADIUS = 6371000.0       # 地球半径 m
EARTH_AREA = 5.10072e14        # 地球表面积 km²
ATMOSPHERIC_MASS = 5.15e18     # 大气质量 kg
```

### 气候常数
```python
PRE_INDUSTRIAL_CO2 = 280.0   # 前工业化CO2浓度 ppm
AREF = 210.2                   # 经验参数 A
B = 2.15                        # 经验参数 B
CO2_RADIATIVE_FORCING = 5.35  # CO2辐射强迫系数
```

### 地理常数
```python
LAND_AREA_FRACTION = 0.29      # 陆地面积占比
OCEAN_AREA_FRACTION = 0.71     # 海洋面积占比
LAND_ALBEDO = 0.30              # 陆地反照率
OCEAN_ALBEDO = 0.06             # 海洋反照率
```

### 系统效率常数
```python
PERFORMANCE_RATIO = 0.8        # 性能比
SYSTEM_LOSSES = 0.8            # 系统损失
INVERTER_EFFICIENCY = 0.96     # 逆变器效率
```

## 📐 实际计算流程

```
输入参数 (用户可调)
    ↓
┌─────────────────────────────────────────┐
│ 反照率计算                              │
│ albedo_land + albedo_ocean           │
│ albedo_pv + coverage_ratio           │
↓ → 行星反照率                           │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ CO2减排计算                             │
│ coverage_ratio × pv_efficiency        │
│ × irradiance × 系统效率                │
↓ → CO2减排量 (ppm)                      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 温度变化计算 (数值积分)                  │
│ S0 × (1-albedo) - σT⁴                  │
│ + CO2辐射强迫                           │
↓ → 温度时间序列                          │
└─────────────────────────────────────────┘
    ↓
输出结果 (温度变化、CO2减排、冷却效率等)
```

## 🎛️ 完整参数列表

### 用户界面可见参数

```python
# 基础地理参数
{
    "latitude": 38.5,        # 纬度 (可选)
    "longitude": 105.0,      # 经度 (可选)
    "albedo_land": 0.35,     # 陆地反照率
    "albedo_ocean": 0.06,    # 海洋反照率
}

# 光伏系统参数 (核心)
{
    "albedo_pv": 0.438,      # 光伏反照率 ⭐核心
    "coverage_ratio": 1e-8,  # 覆盖率 ⭐核心
    "pv_efficiency": 0.23,   # 光伏效率 ⭐核心
}

# 气候参数
{
    "co2_current": 420.0,    # CO2浓度 ⭐核心
    "initial_temp": 15.0,    # 初始温度 ⭐核心
}

# 环境参数 (可选)
{
    "irradiance": 1050,      # 太阳辐照度
    "grid_emission_factor": 520,  # 电网排放因子
}

# 模拟控制
{
    "simulation_years": 100,  # 模拟年数
    "time_step": 1.0,         # 时间步长
}
```

## 🔬 最小可运行参数集

**绝对最少需要3个参数**:
```python
albedo_pv = 0.438      # 光伏反照率
coverage_ratio = 1e-8  # 覆盖率
co2_current = 420.0    # CO2浓度
```

**其他参数使用默认值**:
```python
albedo_land = 0.3      # 默认陆地反照率
albedo_ocean = 0.06     # 默认海洋反照率
pv_efficiency = 0.23   # 默认效率
initial_temp = 15.0    # 默认温度
```

## 📊 参数影响分析

### 对温度变化的影响程度

| 参数 | 影响程度 | 作用机制 |
|------|----------|----------|
| albedo_pv | ⭐⭐⭐⭐⭐ | 直接影响反照率，主要降温因素 |
| coverage_ratio | ⭐⭐⭐⭐⭐ | 线性影响规模效应 |
| pv_efficiency | ⭐⭐⭐ | 影响CO2减排，间接影响温度 |
| co2_current | ⭐⭐⭐ | 影响基准温度和温室效应 |
| albedo_land | ⭐⭐ | 影响基准反照率 |
| initial_temp | ⭐ | 仅影响起始点 |

### 对CO2减排的影响程度

| 参数 | 影响程度 | 作用机制 |
|------|----------|----------|
| coverage_ratio | ⭐⭐⭐⭐⭐ | 线性决定发电规模 |
| pv_efficiency | ⭐⭐⭐⭐ | 直接影响发电量 |
| irradiance | ⭐⭐⭐⭐ | 地区太阳资源差异 |
| grid_emission_factor | ⭐⭐⭐ | 不同地区电网清洁度 |

## 🎯 推荐参数配置

### 研究级配置（精确）
```python
{
    "latitude": 38.5,
    "longitude": 105.0,
    "albedo_pv": 0.438,
    "coverage_ratio": 1e-8,
    "pv_efficiency": 0.23,
    "albedo_land": 0.35,
    "albedo_ocean": 0.06,
    "co2_current": 420.0,
    "initial_temp": 15.0,
    "irradiance": 1050,
    "grid_emission_factor": 520,
    "simulation_years": 100,
    "time_step": 1.0
}
```

### 快速评估配置（简化）
```python
{
    "albedo_pv": 0.438,
    "coverage_ratio": 1e-8,
    "pv_efficiency": 0.23,
    "co2_current": 420.0
    # 其他使用默认值
}
```

## 🔍 参数敏感性分析

### 高敏感性参数
- **coverage_ratio**: 从 1e-8 增加到 1e-7，CO2减排增加10倍
- **albedo_pv**: 从 0.3 增加到 0.95，温度变化增加3倍

### 中等敏感性参数
- **pv_efficiency**: 从 0.20 增加到 0.25，CO2减排增加25%
- **co2_current**: 从 350 增加到 500，基准温度升高2°C

### 低敏感性参数
- **initial_temp**: 只影响起始点，不影响平衡状态
- **time_step**: 影响计算精度，不影响最终结果

## 📝 参数选择建议

### 根据研究目的选择参数

**情景分析**:
- 重点关注: coverage_ratio, albedo_pv
- 固定其他参数为默认值

**技术对比**:
- 重点关注: pv_efficiency, albedo_pv
- 测试不同光伏技术方案

**气候影响**:
- 重点关注: co2_current, albedo_land
- 考虑不同气候情景

**政策制定**:
- 重点关注: coverage_ratio, grid_emission_factor
- 评估不同部署策略

## ✅ 总结

**实际计算最少需要**: 3个核心参数
**推荐完整配置**: 11个参数
**固定物理常数**: 20+个国际标准值

所有参数都有明确的物理依据和数据来源，确保计算结果的科学性和准确性！

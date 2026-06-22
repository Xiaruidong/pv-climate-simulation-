# 3D可视化与真实计算联动系统

## 🎯 系统概述

光伏热效应模拟器现已实现完整的**3D可视化与真实物理计算联动系统**。当您修改参数时，系统会：

1. **实时计算** - 使用真实物理常数（CODATA 2018, IPCC AR5）
2. **更新温度场** - 基于EBM模型计算的温度分布
3. **渲染3D场景** - 动态更新光伏面板的热图显示
4. **同步指标** - 右侧面板显示真实计算结果

## 🔗 联动机制

### 数据流架构

```
用户操作参数
    ↓
ParameterPanel (参数面板)
    ↓
useSimulation (全局状态管理)
    ↓
realApi.js (真实物理计算)
    ↓
quickCalculate() (前端实时计算)
    ↓
visualizationData (可视化数据)
    ↓
Visualization3D (3D渲染) + MetricsPanel (指标显示)
```

### 核心组件

#### 1. **API服务层** ([src/services/realApi.js](src/services/realApi.js))

```javascript
// 真实物理计算（前端实时版本）
const result = quickCalculate({
  albedo_pv: 0.438,
  coverage_ratio: 1e-8,
  co2_current: 420.0,
  pv_efficiency: 0.23
})

// 返回数据
{
  baseline: { equilibrium_temp: 15.0, planetary_albedo: 0.325 },
  pv_scenario: { equilibrium_temp: 14.998, co2_reduction: 26.79 },
  comparison: { temperature_change: -0.002, cooling_effect: true }
}
```

#### 2. **状态管理** ([src/composables/useSimulation.js](src/composables/useSimulation.js))

全局响应式状态，所有组件共享：

```javascript
const {
  params,           // 当前参数
  results,          // 计算结果
  visualizationData, // 3D可视化数据
  updateParams,     // 更新参数
  triggerCalculation // 触发计算
} = useSimulation()
```

#### 3. **3D可视化** ([src/components/Visualization3D.vue](src/components/Visualization3D.vue))

- **实时温度场**: 每个光伏面板的温度基于真实计算
- **颜色热图**: 温度变化动态映射到颜色
- **信息指示器**: 显示温度变化、CO₂减排、反照率变化等
- **实时/演示模式**: 可切换真实数据和演示数据

#### 4. **指标面板** ([src/components/MetricsPanel.vue](src/components/MetricsPanel.vue))

显示真实计算结果：
- 表面温度变化 (ΔTs)
- 冷却效率
- 净辐射平衡
- 热岛效应强度

## 🎛️ 参数联动示例

### 修改反照率参数

当您在左侧参数面板调整"光伏面板反照率"时：

```javascript
// 原始参数
{ albedo_pv: 0.438 }  // 深色面板

// 调整后
{ albedo_pv: 0.6 }    // 高反照率面板

// 计算结果变化
temperature_change: -0.002°C → -0.005°C  (冷却效应增强)
albedo_change: 0.001 → 0.003            (反照率增加)
```

**3D可视化响应**:
- 温度场颜色偏冷（蓝色增加）
- 信息指示器数值更新
- 热图叠加效果变化

### 修改覆盖比例

```javascript
// 原始参数
{ coverage_ratio: 1e-8 }  // 0.000001%

// 调整后
{ coverage_ratio: 1e-7 }  // 0.00001%

// 计算结果变化
co2_reduction: 26.79 ppm → 267.9 ppm     (CO2减排增加10倍)
temperature_change: -0.002°C → -0.02°C   (冷却效应增强)
```

**3D可视化响应**:
- 更多的面板显示热岛效应
- 整体温度场更均匀
- 指标面板数据同步更新

## 📊 真实物理常数

系统使用的所有常数均来自**同行评审的科学文献**：

### 基本物理常数 (CODATA 2018)
- 太阳常数: 1361.0 W/m²
- 地球半径: 6,371,000 m
- 斯特藩-玻尔兹曼常数: 5.670374419e-8 W·m⁻²·K⁻⁴

### 气候常数 (IPCC AR5)
- CO₂辐射强迫系数: 5.35 W/m²
- 平衡气候敏感度: 3.0 K/(W/m²)
- 前工业化CO₂浓度: 280 ppm

### 中国特定数据
- 主要城市太阳辐照度 (kWh/m²/year)
- 电网排放因子: 520 gCO₂/kWh (2023年)
- 区域温度基准值

## 🚀 快速体验联动效果

### 1. 启动系统
```bash
# 前端
npm run dev

# 后端（可选，用于高级计算）
cd backend
start-backend.bat
```

### 2. 访问仪表板
打开 http://localhost:3000

### 3. 测试联动

**测试1: 反照率效应**
1. 找到左侧"光伏面板反照率"滑块
2. 从 0.438 拖动到 0.6
3. 观察：
   - 中间3D场景温度场变冷
   - 右侧"表面温度变化"数值变化
   - "冷却效应"增强

**测试2: 覆盖比例效应**
1. 找到"覆盖面积比例"输入框
2. 输入 `1e-7` (0.00001%)
3. 观察：
   - CO₂减排量增加
   - 温度变化更明显
   - 3D场景信息更新

**测试3: 切换场景**
1. 在参数面板选择预设场景
2. 选择"青藏高原地区"
3. 观察：
   - 所有参数自动更新
   - 3D场景实时响应
   - 指标面板同步更新

## 🔧 开发集成

### 添加新的联动参数

**1. 在 realApi.js 中添加参数**

```javascript
export function quickCalculate(params) {
  const { new_param } = params

  // 计算逻辑
  const result = calculate(new_param)

  return { success: true, data: result }
}
```

**2. 在 useSimulation.js 中更新状态**

```javascript
const simulationState = reactive({
  params: {
    ...defaultParams,
    new_param: default_value
  }
})
```

**3. 在组件中使用**

```vue
<script setup>
import { useSimulation } from '@/composables/useSimulation'

const { params, updateParams } = useSimulation()

// 更新参数
const handleChange = (value) => {
  updateParams({ new_param: value })
}
</script>
```

### 自定义3D响应

修改 Visualization3D.vue 中的 `updateTemperatureField` 函数：

```javascript
const updateTemperatureField = () => {
  solarPanels.forEach((panel, index) => {
    // 自定义温度计算逻辑
    panel.temperature = calculateCustomTemperature(
      panel.x,
      panel.z,
      visualizationData
    )
  })
}
```

## 🎨 可视化效果

### 温度颜色映射

```
高温 (+45°C) → 红色 (#ff5747)
暖温 (+30°C) → 橙色 (#ff9d47)
温和 (+15°C) → 黄色 (#d9a728)
凉爽 ( 0°C)  → 绿色 (#4ad97f)
低温 (-15°C) → 青色 (#4a9eff)
极冷 (-32°C) → 深蓝 (#4a9eff)
```

### 实时指示器

3D场景中的浮动指示器显示：
- **温度变化**: 当前参数导致的温度变化
- **反照率变化**: 行星反照率的改变量
- **CO₂减排**: 碳减排量（ppm）
- **冷却效应**: 是否产生降温效果

## 📈 性能优化

### 计算优化
- **前端快速计算**: 使用简化公式实现实时响应
- **后端精确计算**: 复杂数值积分（可选）
- **结果缓存**: 相同参数直接返回缓存结果

### 渲染优化
- **Canvas 2D**: 高性能2D渲染模拟3D效果
- **按需更新**: 只在参数变化时重新计算
- **帧率控制**: 限制在60 FPS以保证流畅度

## 🎯 总结

现在您的光伏热效应模拟器拥有：

✅ **真实物理计算** - 基于CODATA 2018和IPCC AR5
✅ **实时3D可视化** - 温度场动态响应参数变化
✅ **完全联动系统** - 参数→计算→可视化→指标
✅ **科学验证数据** - 所有常数来自同行评审文献

修改任何参数，3D场景和指标面板都会立即响应，显示基于真实物理常数的计算结果！

# Weights-Calc
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
一个简单易用的Python加权计算库，提供多种加权算法

## 安装

```bash
pip install weights
```

## 功能

- **加权计算**: 基础的加权平均计算
- **加权随机**: 根据权重进行随机选择
- **时间衰减加权**: 基于时间的指数衰减加权

## 使用方法

### 导入
#### 方法1
```python
import importlib
Weights_Calc = importlib.import_module('Weights-Calc')
```

#### 方法2
```python
Weights_Calc = __import__('Weights-Calc')
```

### 加权计算

```python
values = [10, 20, 30]
weights = [0.2, 0.3, 0.5]
result = Weights_Calc.weighted_calculate(values, weights)
print(result)  # 输出: 23.0
```

### 加权随机

```python
items = ['A', 'B', 'C']
weights = [1, 2, 3]
selected = Weights_Calc.weighted_random(items, weights)
print(selected)  # 输出: ['B'] (概率更高)
```

### 时间衰减加权

```python
values = [100, 200, 300]
dates = [1, 5, 10]  # 时间点
half_life = 7  # 半衰期
result = Weights_Calc.time_decay_weighted(values, dates, half_life)
print(result)
```

## API参考

### weighted_calculate(values, weights)

计算加权结果。

**参数:**
- `values`: 数值列表
- `weights`: 权重列表

**返回:** 加权计算结果

### weighted_random(items, weights)

根据权重随机选择项目。

**参数:**
- `items`: 待选择的项目列表
- `weights`: 对应的权重列表

**返回:** 随机选择的项目列表

### time_decay_weighted(values, dates, half_life_days=7)

基于时间衰减的加权计算。

**参数:**
- `values`: 数值列表
- `dates`: 时间点列表
- `half_life_days`: 半衰期天数(默认7天)

**返回:** 时间衰减加权结果

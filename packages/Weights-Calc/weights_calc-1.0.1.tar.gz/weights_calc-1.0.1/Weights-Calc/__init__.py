import random
import math

__version__ = "1.0.1"

def weighted_calculate(values: list[float], weights: list[float]):
    """加权计算"""
    if len(values) != len(weights):
        raise ValueError("数值和权重数量必须相同")
    
    res = 0
    for i in range(len(values)):
        res += values[i] * weights[i]
    return res


def weighted_random(items: list[float], weights: list[float]):
    """加权随机"""
    return random.choices(items, weights=weights)

def time_decay_weighted(values, dates, half_life_days=7):
    """时间衰减加权"""
    latest_date = max(dates)
    time_diffs = [latest_date - date for date in dates]
    
    # 指数衰减权重：半衰期公式
    decay_factor = math.log(2) / half_life_days
    weights = [math.exp(-decay_factor * diff) for diff in time_diffs]
    
    # 使用核心加权计算函数
    return weighted_calculate(values, weights)

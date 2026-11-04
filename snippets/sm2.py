"""
SuperMemo-2 间隔重复调度（节选）
==============================
从学习系统的记忆调度模块中摘出的纯函数：不含数据库、不含 UI、无外部依赖，
因此可以直接单测。间隔与难度因子的迭代完全遵循 SM-2 原始论文。
"""

from typing import Tuple


def calculate_sm2_interval(
    quality: int,
    repetition: int,
    interval: int,
    ease_factor: float,
) -> Tuple[int, int, float, int]:
    """
    执行一次标准 SM-2 迭代。

    :param quality: 用户自评回忆质量 (1-5)，低于 3 视为回忆失败
    :param repetition: 历史连续成功复习次数
    :param interval: 当前复习间隔（天）
    :param ease_factor: 当前难度因子 EF，物理下限 1.3
    :return: (新连续次数, 新间隔天数, 新难度因子, 掌握度等级)
    """
    # 评分约束到 1-5，越界输入不得影响状态机
    q = max(1, min(5, int(quality)))

    if q < 3:
        # 回忆失败：重置连续计数，次日重来
        new_repetition = 0
        new_interval = 1
    else:
        # 回忆成功：前两次固定 1 天、6 天，之后按 EF 递增
        if repetition == 0:
            new_interval = 1
        elif repetition == 1:
            new_interval = 6
        else:
            new_interval = int(round(interval * ease_factor))
        new_repetition = repetition + 1

    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    diff = 5 - q
    new_ef = ease_factor + (0.1 - diff * (0.08 + diff * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    # 掌握度：0 陌生 / 1 初识 / 2 熟练 / 3 牢固
    if new_repetition == 0:
        mastery_level = 0
    elif new_repetition == 1:
        mastery_level = 1
    elif new_repetition == 2:
        mastery_level = 2
    else:
        mastery_level = 3 if (q >= 4 and new_interval >= 12) else 2

    return new_repetition, new_interval, round(new_ef, 2), mastery_level


if __name__ == "__main__":
    # 连续三次高质量回忆：间隔 1 → 6 → 15(≈6×2.5)
    rep, ivl, ef, level = 0, 0, 2.5, 0
    for _ in range(3):
        rep, ivl, ef, level = calculate_sm2_interval(5, rep, ivl, ef)
        print(f"rep={rep} interval={ivl}d ef={ef} mastery={level}")

    # 一次回忆失败：立即回到 1 天，EF 被扣分但不低于 1.3
    print(calculate_sm2_interval(2, rep, ivl, ef))

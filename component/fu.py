import random
from .output import get_output
from . import character as charmod


def fu_check(attr1: str, attr2: str, difficulty: int, user_id: str = None, name: str = None):
    """
    最终物语（fu）掷骰检定规则实现：
    - 掷两枚 d10，较高为希望骰，较低为恐惧骰
    - 若两枚相同且 >=6 => 大成功（忽视难度）
    - 若两枚都是 1 => 大失败
    - 否则以两枚之和与难度比较（使用 >= 判定为成功），并根据 希望骰>恐惧骰 决定“希望”或“恐惧”的性质
    返回格式化的输出字符串（通过 get_output 的 `fu.check` 模板）
    """
    try:
        difficulty = int(difficulty)
    except Exception:
        return get_output("fu.check.error", error=f"invalid difficulty: {difficulty}")

    # 解析或读取属性值：如果参数为数字则直接使用，否则尝试从人物卡读取
    def resolve_attr_value(arg):
        if arg is None:
            return 0
        s = str(arg).strip()
        if s.isdigit():
            return int(s)
        if user_id:
            try:
                return int(charmod.get_skill_value(user_id, s))
            except Exception:
                return 0
        return 0

    v1 = resolve_attr_value(attr1)
    v2 = resolve_attr_value(attr2)

    if v1 <= 0 or v2 <= 0:
        return get_output("fu.check.error", error=f"invalid attribute values: {v1}, {v2}")

    # 分配希望/恐惧：属性值更高者为希望（相等时以 attr1 为希望）
    if v1 >= v2:
        hope_attr, hope_max, fear_attr, fear_max = attr1, v1, attr2, v2
        hope_roll = random.randint(1, hope_max)
        fear_roll = random.randint(1, fear_max)
    else:
        hope_attr, hope_max, fear_attr, fear_max = attr2, v2, attr1, v1
        hope_roll = random.randint(1, hope_max)
        fear_roll = random.randint(1, fear_max)

    d1 = hope_roll
    d2 = fear_roll
    total = d1 + d2

    # 大失败（两个1）
    if d1 == 1 and d2 == 1:
        return get_output(
            "fu.check.great_failure",
            name=name or "",
            d1=d1,
            d2=d2,
        )

    # 大成功（两个一样且 >=6）
    if d1 == d2 and d1 >= 6:
        return get_output(
            "fu.check.great_success",
            name=name or "",
            d1=d1,
            d2=d2,
        )

    # 平局（相同点数但未触发大成功）
    if d1 == d2:
        return get_output(
            "fu.check.tie",
            name=name or "",
            attribute1=attr1,
            attribute2=attr2,
            d1=d1,
            d2=d2,
            total=total,
            difficulty=difficulty,
        )

    # 成功判定（使用 >= 作为成功条件）
    success = total >= difficulty

    # 根据掷出点数判断希望/恐惧
    if d1 > d2:
        # hope is d1
        if success:
            return get_output(
                "fu.check.hope_success",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                d1=d1,
                d2=d2,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
            )
        else:
            return get_output(
                "fu.check.hope_failure",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                d1=d1,
                d2=d2,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
            )
    else:
        # fear is d2 (d1 < d2)
        if success:
            return get_output(
                "fu.check.fear_success",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                d1=d1,
                d2=d2,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
            )
        else:
            return get_output(
                "fu.check.fear_failure",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                d1=d1,
                d2=d2,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
            )

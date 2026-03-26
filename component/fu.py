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


    # ----------------- 命刻系统（Marks） -----------------
    # 提供：新增命刻、显示命刻、推进/回退命刻、删除命刻

    class Mark:
        def __init__(self, name: str, length: int):
            self.name = str(name)
            self.length = int(length)
            self.progress = 0

        def is_completed(self):
            return self.progress >= self.length


    # 全局命刻列表（按创建顺序）
    marks = []  # list[Mark]


    def _render_progress_bar(mark: Mark) -> str:
        filled = max(0, min(mark.progress, mark.length))
        empty = max(0, mark.length - filled)
        # 实心方块/空心方块
        return "".join(["■" for _ in range(filled)] + ["□" for _ in range(empty)])


    def create_mark(name: str, length: int) -> str:
        """新增命刻，初始进度为0。返回确认信息字符串。"""
        try:
            length = int(length)
        except Exception:
            return get_output("fu.mark.advance.invalid_delta", delta=length)
        if length <= 0:
            return get_output("fu.mark.advance.invalid_delta", delta=length)
        m = Mark(name, length)
        marks.append(m)
        return get_output("fu.mark.create", name=m.name, bar=_render_progress_bar(m), progress=m.progress, length=m.length)


    def show_marks() -> str:
        """显示当前所有命刻的状态。"""
        if not marks:
            return get_output("fu.mark.show.empty")
        lines = []
        for idx, m in enumerate(marks, start=1):
            status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
            lines.append(f"{idx}. {m.name}\n{_render_progress_bar(m)} {status}")
        return get_output("fu.mark.show.list", text="\n\n".join(lines))


    def _find_mark(identifier):
        """根据序号（1-based）或名称查找命刻，返回 (index, mark) 或 (None, None)。"""
        if identifier is None:
            return None, None
        # 尝试按序号
        try:
            i = int(identifier)
            if 1 <= i <= len(marks):
                return i - 1, marks[i - 1]
        except Exception:
            pass
        # 按名称匹配（精确匹配）
        for i, m in enumerate(marks):
            if m.name == identifier:
                return i, m
        # 忽略大小写的匹配
        for i, m in enumerate(marks):
            if m.name.lower() == str(identifier).lower():
                return i, m
        return None, None


    def advance_mark(identifier, delta: int) -> str:
        """推进或回退某个命刻，identifier 可为序号或名称，delta 可为正/负整数。返回该命刻进度条字符串或错误信息。"""
        try:
            delta = int(delta)
        except Exception:
            return get_output("fu.mark.advance.invalid_delta", delta=delta)
        idx, m = _find_mark(identifier)
        if m is None:
            return get_output("fu.mark.advance.not_found", identifier=identifier)
        m.progress += delta
        if m.progress < 0:
            m.progress = 0
        if m.progress > m.length:
            m.progress = m.length
        status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
        return get_output("fu.mark.advance.updated", name=m.name, bar=_render_progress_bar(m), status=status)


    def delete_mark(identifier) -> str:
        """删除指定命刻，identifier 可为序号、名称或特殊字符串 '已完成'（删除所有已完成的命刻）。"""
        if identifier == "已完成":
            before = len(marks)
            remaining = [m for m in marks if not m.is_completed()]
            removed = before - len(remaining)
            marks.clear()
            marks.extend(remaining)
            return get_output("fu.mark.delete.removed_completed", count=removed)
        idx, m = _find_mark(identifier)
        if m is None:
            return get_output("fu.mark.delete.not_found", identifier=identifier)
        # 删除
        del marks[idx]
        return get_output("fu.mark.delete.removed", name=m.name)


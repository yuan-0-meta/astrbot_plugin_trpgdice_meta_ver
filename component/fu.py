import random
from .output import get_output
from . import character as charmod


def fu_check(attr1: str, attr2: str, difficulty: int, user_id: str = None, name: str = None):
    """
    最终物语（fu）掷骰检定规则实现：
    - 掷两枚骰子，较大为希望骰，较小为恐惧骰
    - 若两枚相同且 >=6 => 大成功（忽视难度）
    - 若两枚都是 1 => 大失败
    - 否则以两枚之和与难度比较（使用 >= 判定为成功），并根据 希望骰>恐惧骰 决定“希望”或“恐惧”的性质
    - 返回格式化的输出字符串（通过 get_output 的 `fu.check` 模板）
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

    """参数解释，不然我自己看不懂了。attr1 和 attr2 可以是直接的数值字符串（如 "8"）或属性名称（如 "力量"），
        如果是属性名称则会尝试从人物卡中读取对应属性值（如果 user_id 提供且属性存在）。
        v1,v2 是解析后的属性值，必须为正整数，否则视为无效输入并返回错误信息。
        根据 v1 和 v2 的大小关系确定哪个是希望属性，哪个是恐惧属性，并进行掷骰和结果判定。
        hope_attr, hope_max, fear_attr, fear_max 分别记录希望和恐惧的属性名称及其数值上限，用于输出模板中的变量替换。
        hope_dice 和 fear_dice 是两枚骰子的结果，hope_dice是希望骰，fear_dice是恐惧骰，total 是它们的和，high_die 和 low_die 分别是较大和较小的骰子结果。
        根据掷骰结果判断是否触发大成功、大失败、平局、希望成功/失败，并返回相应的输出字符串。
    """

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

    hope_dice = hope_roll
    fear_dice = fear_roll
    total = hope_dice + fear_dice

    if hope_dice > fear_dice:
        high_dice = hope_dice
        low_dice = fear_dice
    else:
        high_dice = fear_dice
        low_dice = hope_dice

    # 大失败（两个1）
    if hope_dice == 1 and fear_dice == 1:
        return get_output(
            "fu.check.great_failure",
            name=name or "",
            hope_dice=hope_dice,
            fear_dice=fear_dice,
        )

    # 大成功（两个一样且 >=6）
    if hope_dice == fear_dice and hope_dice >= 6:
        return get_output(
            "fu.check.great_success",
            name=name or "",
            hope_dice=hope_dice,
            fear_dice=fear_dice,
        )

    # 平局（相同点数但未触发大成功）
    if hope_dice == fear_dice:
        return get_output(
            "fu.check.tie",
            name=name or "",
            attribute1=attr1,
            attribute2=attr2,
            hope_dice=hope_dice,
            fear_dice=fear_dice,
            total=total,
            difficulty=difficulty,
        )

    # 成功判定（使用 >= 作为成功条件）
    success = total >= difficulty

    # 根据掷出点数判断希望/恐惧
    if hope_dice > fear_dice:
        # hope is hope_dice
        if success:
            return get_output(
                "fu.check.hope_success",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                hope_dice=hope_dice,
                fear_dice=fear_dice,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
                high_dice=high_dice,
                low_dice=low_dice,
            )
        else:
            return get_output(
                "fu.check.hope_failure",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                hope_dice=hope_dice,
                fear_dice=fear_dice,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
                high_dice=high_dice,
                low_dice=low_dice,
            )
    else:
        # fear is fear_dice (hope_dice < fear_dice)
        if success:
            return get_output(
                "fu.check.fear_success",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                hope_dice=hope_dice,
                fear_dice=fear_dice,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
                high_die=high_dice,
                low_die=low_dice,

            )
        else:
            return get_output(
                "fu.check.fear_failure",
                name=name or "",
                attribute1=attr1,
                attribute2=attr2,
                hope_dice=hope_dice,
                fear_dice=fear_dice,
                hope_attr=hope_attr,
                fear_attr=fear_attr,
                hope=hope_max,
                fear=fear_max,
                total=total,
                difficulty=difficulty,
                high_dice=high_dice,
                low_dice=low_dice,
            )
    # ----------------- 命刻系统 -----------------
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


def show_marks(identifier: str = "") -> str:
    """显示当前所有命刻的状态。支持传入 identifier 进行过滤/精确查找。
    当 identifier 为空时返回全部命刻；当匹配单项时返回单条模板；匹配多项时返回列表模板。"""
    if not marks:
        return get_output("fu.mark.show.empty")
    lines = []
    if identifier:
        matches = _find_mark(identifier)
        if not matches:
            return get_output("fu.mark.show.not_found", identifier=identifier)
        if len(matches) == 1:
            _, m = matches[0]
            status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
            return get_output("fu.mark.show.single", name=m.name, bar=_render_progress_bar(m), status=status)
        # 多个匹配，列出匹配项
        for idx, m in matches:
            status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
            lines.append(f"{idx+1}. {m.name}\n{_render_progress_bar(m)} {status}")
        return get_output("fu.mark.show.list", text="\n\n".join(lines))
    for idx, m in enumerate(marks, start=1):
        status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
        lines.append(f"{idx}. {m.name}\n{_render_progress_bar(m)} {status}")
    return get_output("fu.mark.show.list", text="\n\n".join(lines))


def _find_mark(identifier):
    """根据序号（1-based）或名称查找命刻，返回匹配列表 [(index, mark), ...]。"""
    results = []
    if identifier is None or identifier == "":
        return results
    s = str(identifier)
    # 尝试按序号（优先）
    try:
        i = int(s)
        if 1 <= i <= len(marks):
            return [(i - 1, marks[i - 1])]
    except Exception:
        pass

    # 精确匹配（区分大小写）
    for i, m in enumerate(marks):
        if m.name == s:
            results.append((i, m))
    if results:
        return results

    # 精确匹配（不区分大小写）
    low = s.lower()
    for i, m in enumerate(marks):
        if m.name.lower() == low:
            results.append((i, m))
    if results:
        return results

    # 模糊包含匹配（不区分大小写）——返回所有包含 identifier 的命刻
    for i, m in enumerate(marks):
        if low in m.name.lower():
            results.append((i, m))
    return results


def advance_mark(identifier, delta: int) -> str:
    """推进或回退某个命刻，identifier 可为序号或名称，delta 可为正/负整数。返回该命刻进度条字符串或错误信息。"""
    try:
        delta = int(delta)
    except Exception:
        return get_output("fu.mark.advance.invalid_delta", delta=delta)
    matches = _find_mark(identifier)
    if not matches:
        return get_output("fu.mark.advance.not_found", identifier=identifier)

    texts = []
    for identifier, m in matches:
        m.progress += delta
        if m.progress < 0:
            m.progress = 0
        if m.progress > m.length:
            m.progress = m.length
        status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
        texts.append(get_output("fu.mark.advance.updated", name=m.name, bar=_render_progress_bar(m), status=status))

    # 如果只有一项匹配，则返回单条模板；否则将多条结果用空行分隔返回
    return "\n\n".join(texts)


def delete_mark(identifier) -> str:
    """删除指定命刻，identifier 可为序号、名称或特殊字符串 '已完成'（删除所有已完成的命刻）。"""
    if identifier == "已完成":
        before = len(marks)
        remaining = [m for m in marks if not m.is_completed()]
        removed = before - len(remaining)
        marks.clear()
        marks.extend(remaining)
        return get_output("fu.mark.delete.removed_multiple", count=removed, name="已完成")
    matches = _find_mark(identifier)
    if not matches:
        return get_output("fu.mark.delete.not_found", identifier=identifier)

    # 删除所有匹配的项（使用索引集合防止删除时错位）
    remove_idxs = set(i for i, _ in matches)
    removed_names = [m.name for _, m in matches]
    remaining = [m for i, m in enumerate(marks) if i not in remove_idxs]
    removed_count = len(marks) - len(remaining)
    marks.clear()
    marks.extend(remaining)

    if removed_count == 1:
        return get_output("fu.mark.delete.removed", name=removed_names[0])
    else:
        # 若删除多项，返回数量与被删除项名列表
        return get_output("fu.mark.delete.removed_multiple", count=removed_count, name=", ".join(removed_names))


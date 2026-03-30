import random
from .output import get_output
from . import character as charmod

# 模块级活动群，用于按群隔离命刻与人物卡访问
_active_group = None
# 命刻按群组隔离存储：{ group_id_str: [Mark, ...] }
marks_by_group = {}


def set_active_group(group_id):
    global _active_group
    _active_group = group_id


def _get_marks_for_group():
    key = str(_active_group) if _active_group is not None else "_global"
    if key not in marks_by_group:
        marks_by_group[key] = []
    return marks_by_group[key]


def fu_check(attr1: str, attr2: str, difficulty: int, user_id: str = None, name: str = None):
    """
    最终物语（fu）掷骰检定规则实现。
    - 掷两枚骰子，较大为希望骰，较小为恐惧骰
    - 两枚相同且 >=6 为大成功；两枚均为1为大失败；否则比较两骰之和与难度
    返回格式化字符串（使用 output 模板）。
    """
    try:
        difficulty = int(difficulty)
    except Exception:
        return get_output("fu.check.error", error=f"invalid difficulty: {difficulty}")

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

    # 按属性高低决定 hope/fear
    if v1 >= v2:
        hope_attr, hope_max, fear_attr, fear_max = attr1, v1, attr2, v2
    else:
        hope_attr, hope_max, fear_attr, fear_max = attr2, v2, attr1, v1

    hope_roll = random.randint(1, max(1, hope_max))
    fear_roll = random.randint(1, max(1, fear_max))

    hope_dice = hope_roll
    fear_dice = fear_roll
    total = hope_dice + fear_dice

    high_dice = max(hope_dice, fear_dice)
    low_dice = min(hope_dice, fear_dice)

    # 大失败
    if hope_dice == 1 and fear_dice == 1:
        return get_output("fu.check.great_failure", name=name or "", hope_dice=hope_dice, fear_dice=fear_dice)

    # 大成功
    if hope_dice == fear_dice and hope_dice >= 6:
        return get_output("fu.check.great_success", name=name or "", hope_dice=hope_dice, fear_dice=fear_dice)

    # 平局（但未大成功）
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

    success = total >= difficulty

    if hope_dice > fear_dice:
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
class Mark:
    def __init__(self, name: str, length: int):
        self.name = str(name)
        self.length = int(length)
        self.progress = 0

    def is_completed(self):
        return self.progress >= self.length


def _render_progress_bar(mark: Mark) -> str:
    filled = max(0, min(mark.progress, mark.length))
    empty = max(0, mark.length - filled)
    return "".join(["■" for _ in range(filled)] + ["□" for _ in range(empty)])


def create_mark(name: str, length: int) -> str:
    try:
        length = int(length)
    except Exception:
        return get_output("fu.mark.advance.invalid_delta", delta=length)
    if length <= 0:
        return get_output("fu.mark.advance.invalid_delta", delta=length)
    m = Mark(name, length)
    marks = _get_marks_for_group()
    marks.append(m)
    return get_output("fu.mark.create", name=m.name, bar=_render_progress_bar(m), progress=m.progress, length=m.length)


def show_marks(identifier: str = "") -> str:
    marks = _get_marks_for_group()
    if not marks:
        return get_output("fu.mark.show.empty")
    lines = []
    if identifier:
        matches = _find_mark(identifier, marks)
        if not matches:
            return get_output("fu.mark.show.not_found", identifier=identifier)
        if len(matches) == 1:
            _, m = matches[0]
            status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
            return get_output("fu.mark.show.single", name=m.name, bar=_render_progress_bar(m), status=status)
        for idx, m in matches:
            status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
            lines.append(f"{idx+1}. {m.name}\n{_render_progress_bar(m)} {status}")
        return get_output("fu.mark.show.list", text="\n\n".join(lines))
    for idx, m in enumerate(marks, start=1):
        status = "(已完成)" if m.is_completed() else f"({m.progress}/{m.length})"
        lines.append(f"{idx}. {m.name}\n{_render_progress_bar(m)} {status}")
    return get_output("fu.mark.show.list", text="\n\n".join(lines))


def _find_mark(identifier, marks_list):
    results = []
    if identifier is None or identifier == "":
        return results
    s = str(identifier)
    try:
        i = int(s)
        if 1 <= i <= len(marks_list):
            return [(i - 1, marks_list[i - 1])]
    except Exception:
        pass
    for i, m in enumerate(marks_list):
        if m.name == s:
            results.append((i, m))
    if results:
        return results
    low = s.lower()
    for i, m in enumerate(marks_list):
        if m.name.lower() == low:
            results.append((i, m))
    if results:
        return results
    for i, m in enumerate(marks_list):
        if low in m.name.lower():
            results.append((i, m))
    return results


def advance_mark(identifier, delta: int) -> str:
    try:
        delta = int(delta)
    except Exception:
        return get_output("fu.mark.advance.invalid_delta", delta=delta)
    marks = _get_marks_for_group()
    matches = _find_mark(identifier, marks)
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
    return "\n\n".join(texts)


def delete_mark(identifier) -> str:
    marks = _get_marks_for_group()
    if identifier == "已完成":
        before = len(marks)
        remaining = [m for m in marks if not m.is_completed()]
        removed = before - len(remaining)
        marks.clear()
        marks.extend(remaining)
        return get_output("fu.mark.delete.removed_multiple", count=removed, name="已完成")
    matches = _find_mark(identifier, marks)
    if not matches:
        return get_output("fu.mark.delete.not_found", identifier=identifier)
    remove_idxs = set(i for i, _ in matches)
    removed_names = [m.name for _, m in matches]
    remaining = [m for i, m in enumerate(marks) if i not in remove_idxs]
    removed_count = len(marks) - len(remaining)
    marks.clear()
    marks.extend(remaining)
    if removed_count == 1:
        return get_output("fu.mark.delete.removed", name=removed_names[0])
    else:
        return get_output("fu.mark.delete.removed_multiple", count=removed_count, name=", ".join(removed_names))


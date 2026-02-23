import yaml
import os
import random

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default_config.yaml")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()

def get_output(key: str, **kwargs):
    """
    支持多层 key，通过点分隔，如 "skill_check.normal"
    根据 key 获取输出模板，并用 kwargs 格式化。
    如果 key 不存在则返回空字符串。
    """
    keys = key.split(".")
    template = _config.get("output", {})
    for k in keys:
        template = template.get(k, {})

    # 如果配置中未找到对应 key，template 可能是空 dict
    if isinstance(template, dict) and not template:
        raise ValueError(f"{key} cannot be found in config.yaml")

    # 支持字符串或字符串列表。如果是列表，从中随机选择一项（均等概率）
    chosen = None
    if isinstance(template, list):
        if not template:
            raise ValueError(f"{key} has an empty list in config.yaml")
        chosen = random.choice(template)
    elif isinstance(template, str):
        chosen = template
    else:
        raise ValueError(f"{key} has unsupported type in config.yaml: {type(template)}")

    try:
        return chosen.format(**kwargs)
    except Exception:
        return chosen

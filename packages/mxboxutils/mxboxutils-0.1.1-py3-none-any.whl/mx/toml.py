import tomllib
import os
from pathlib import Path


def get_toml_value(file_path: str | Path, key_path: str | list[str], default=None):
    """
    加载TOML文件并获取指定路径的值

    参数:
        file_path (str | Path): TOML文件的路径，可以是字符串或Path对象
        key_path (str | list[str]): 要获取的值的键路径，可以是点分隔的字符串或键列表
        default: 如果键不存在时返回的默认值

    返回:
        获取到的值或默认值
    """
    # 确保file_path是字符串
    file_path_str = str(file_path) if isinstance(file_path, Path) else file_path

    if not os.path.exists(file_path_str):
        return default

    try:
        with open(file_path_str, "rb") as f:
            data = tomllib.load(f)

        # 处理键路径
        if isinstance(key_path, str):
            keys = key_path.split(".")
        else:
            keys = key_path

        # 遍历键路径获取值
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
    except Exception:
        return default


def load_toml(filepath):
    if not os.path.exists(filepath):
        return None

    with open(filepath, "rb") as f:
        return tomllib.load(f)

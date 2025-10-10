import os
import tomllib


def load_toml(filepath):
    if not os.path.exists(filepath):
        return None

    with open(filepath, "rb") as f:
        return tomllib.load(f)

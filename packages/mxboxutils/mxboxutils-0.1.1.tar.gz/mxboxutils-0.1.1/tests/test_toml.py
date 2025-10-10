import tempfile
from pathlib import Path

from mx.toml import get_toml_value

def test_get_toml_value():
        # 创建临时TOML文件用于测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 简化的TOML内容，避免格式问题
            toml_content = """
            title = "TOML Example"
            
            [owner]
            name = "Tom Preston-Werner"
            age = 45
            
            [database]
            enabled = true
            ports = [8000, 8001, 8002]
            """
            
            # 写入临时TOML文件
            temp_file = Path(temp_dir) / "test_config.toml"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(toml_content)
            
            # 测试基本值获取
            assert get_toml_value(temp_file, "title") == "TOML Example"
            assert get_toml_value(temp_file, "owner.name") == "Tom Preston-Werner"
            assert get_toml_value(temp_file, "owner.age") == 45
            assert get_toml_value(temp_file, "database.enabled") is True
            
            # 测试使用列表作为键路径
            assert get_toml_value(temp_file, ["owner", "name"]) == "Tom Preston-Werner"
            
            # 测试数组
            ports = get_toml_value(temp_file, "database.ports")
            assert isinstance(ports, list)
            assert len(ports) == 3
            assert ports[0] == 8000
            
            # 测试不存在的键
            assert get_toml_value(temp_file, "non_existent_key") is None
            assert get_toml_value(temp_file, "non_existent_key", "default_value") == "default_value"
            assert get_toml_value(temp_file, "owner.non_existent_key") is None
            
            # 测试不存在的文件
            non_existent_file = Path(temp_dir) / "non_existent.toml"
            assert get_toml_value(non_existent_file, "any_key") is None
            assert get_toml_value(non_existent_file, "any_key", "default_for_missing_file") == "default_for_missing_file"
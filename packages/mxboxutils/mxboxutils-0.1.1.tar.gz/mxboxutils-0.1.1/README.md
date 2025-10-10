# MxBoxUtils

MxBoxUtils 是一个Python工具库，提供了多种实用功能，包括文件操作、网络工具、TOML配置解析等功能。

## 目录结构

```
MxBoxUtils/
├── src/
│   ├── mx/             # 核心功能模块
│   │   ├── file.py     # 文件操作工具
│   │   ├── image.py    # 图像处理工具
│   │   ├── net.py      # 网络相关工具
│   │   ├── pdf.py      # PDF处理工具
│   │   └── toml.py     # TOML配置文件解析工具
│   └── mxboxutils/     # 扩展功能模块
└── tests/              # 测试文件目录
```

## 功能模块

### 1. 文件操作 (file.py)

提供文件和目录操作相关的功能。

#### all_files(f_path: str, recursive: bool = False) -> list[str]
列出指定目录下的所有文件名。
- **参数**: 
  - `f_path` - 目录路径
  - `recursive` - 是否递归扫描子目录，默认为False
- **返回值**: 包含所有文件名的列表

#### all_images(f_path: str, f_ext: list[str], recursive: bool = False) -> list[str]
列出指定目录下的所有指定类型的图片文件。
- **参数**: 
  - `f_path` - 目录路径
  - `f_ext` - 要匹配的文件扩展名列表（不包含点号）
  - `recursive` - 是否递归扫描子目录，默认为False
- **返回值**: 包含所有匹配文件的列表

### 2. 网络工具 (net.py)

提供网络相关功能，包括WiFi信息获取和局域网设备扫描。

#### get_wifi_networks() -> List[Dict[str, Any]]
获取所有可用WiFi热点信息（仅支持Windows系统）。
- **返回值**: 包含WiFi热点信息的列表，每个字典包含以下键：
  - `ssid`: WiFi名称
  - `signal_strength`: 信号强度（百分比）
  - `bssid`: 接入点MAC地址
  - `channel`: 信道号
  - `authentication`: 认证方式
  - `encryption`: 加密方式

#### get_local_network_devices() -> List[Dict[str, Any]]
获取本地局域网中的所有主机设备信息。
- **返回值**: 包含局域网设备信息的列表，每个字典可能包含以下键：
  - `ip_address`: IP地址
  - `mac_address`: MAC地址
  - `manufacturer`: 设备制造商（如果可识别）
  - `hostname`: 主机名（如果可解析）

#### 辅助函数
- `get_local_ip() -> Optional[str]`: 获取本地主机的IP地址
- `get_local_network(local_ip: str) -> Optional[ipaddress.IPv4Network]`: 根据本地IP地址确定局域网范围
- `ping_host(ip: str) -> bool`: Ping指定的IP地址，检查主机是否在线
- `scan_network(network: ipaddress.IPv4Network, max_workers: int = 100) -> List[str]`: 使用多线程ping扫描局域网中的所有主机
- `get_mac_address(ip: str) -> Optional[str]`: 获取指定IP地址的MAC地址
- `get_hostname(ip: str) -> Optional[str]`: 尝试通过IP地址解析主机名
- `get_manufacturer_from_mac(mac: str) -> Optional[str]`: 尝试从MAC地址获取设备制造商信息

### 3. TOML配置解析 (toml.py)

提供TOML配置文件解析功能。

#### get_toml_value(file_path: str | Path, key_path: str | list[str], default=None)
加载TOML文件并获取指定路径的值。
- **参数**: 
  - `file_path` - TOML文件的路径，可以是字符串或Path对象
  - `key_path` - 要获取的值的键路径，可以是点分隔的字符串或键列表
  - `default` - 如果键不存在时返回的默认值
- **返回值**: 获取到的值或默认值

### 4. 图像处理 (image.py)

预留模块，暂无实现。

### 5. PDF处理 (pdf.py)

预留模块，暂无实现。

## 安装说明

```bash
# 从源代码安装
git clone [仓库地址]
cd MxBoxUtils
pip install -e .
```

## 版本信息

当前版本: 0.1.0

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License
import platform
import re
import socket
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional


def get_wifi_networks() -> List[Dict[str, Any]]:
    """获取所有可用WiFi热点信息

    Returns:
        List[Dict[str, Any]]: 包含所有WiFi热点信息的列表，每个字典包含SSID、信号强度、加密方式等信息
    """  # noqa: W293
    # 检查操作系统是否为Windows
    if platform.system() != "Windows":
        raise OSError("此函数仅支持Windows操作系统")
    # noqa: W293
    try:
        # 执行netsh命令获取WiFi列表
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=Bssid"],
            capture_output=True,
            text=True,
            check=True,
        )
        # noqa: W293
        # 解析输出结果
        output = result.stdout
        networks = []
        current_network = {}

        # 逐行解析输出
        for line in output.splitlines():
            line = line.strip()

            # 新网络的开始
            if line.startswith("SSID") and ":" in line:
                # 如果已经有收集的网络信息，添加到列表中
                if current_network:
                    networks.append(current_network)
                    current_network = {}

                # 提取SSID
                ssid_match = re.search(r"SSID (\d+) : (.+)", line)
                if ssid_match:
                    current_network["ssid"] = ssid_match.group(2)

            # 提取信号强度
            elif line.startswith("Signal") and ":" in line:
                signal_match = re.search(r"Signal\s*:\s*(\d+)%", line)
                if signal_match:
                    current_network["signal_strength"] = int(signal_match.group(1))

            # 提取BSSID
            elif "BSSID" in line and ":" in line:
                bssid_match = re.search(r"BSSID\s+(\d+)\s*:\s*(.+)", line)
                if bssid_match:
                    current_network["bssid"] = bssid_match.group(2)

            # 提取频道
            elif line.startswith("Channel") and ":" in line:
                channel_match = re.search(r"Channel\s*:\s*(\d+)", line)
                if channel_match:
                    current_network["channel"] = int(channel_match.group(1))

            # 提取加密方式
            elif line.startswith("Authentication") and ":" in line:
                auth_match = re.search(r"Authentication\s*:\s*(.+)", line)
                if auth_match:
                    current_network["authentication"] = auth_match.group(1)

            # 提取加密算法
            elif line.startswith("Encryption") and ":" in line:
                encryption_match = re.search(r"Encryption\s*:\s*(.+)", line)
                if encryption_match:
                    current_network["encryption"] = encryption_match.group(1)

        # 添加最后一个网络
        if current_network:
            networks.append(current_network)

        return networks

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"执行netsh命令失败: {e}")
    except Exception as e:
        raise RuntimeError(f"获取WiFi热点信息时发生错误: {e}")


def get_local_network_devices() -> List[Dict[str, Any]]:
    """获取本地局域网中的所有主机设备信息

    Returns:
        List[Dict[str, Any]]: 包含局域网中所有设备信息的列表，每个字典包含IP地址、MAC地址、主机名等信息
    """
    devices = []
    
    try:
        # 获取本地IP地址和子网信息
        local_ip = get_local_ip()
        if not local_ip:
            raise RuntimeError("无法获取本地IP地址")
        
        # 计算局域网IP范围
        network = get_local_network(local_ip)
        if not network:
            raise RuntimeError("无法确定局域网范围")
        
        # 使用多线程ping扫描局域网
        live_hosts = scan_network(network)
        
        # 获取设备的MAC地址和主机名
        for ip in live_hosts:
            device_info = {
                "ip_address": ip
            }
            
            # 获取MAC地址
            mac_address = get_mac_address(ip)
            if mac_address:
                device_info["mac_address"] = mac_address
                
                # 尝试获取制造商信息
                manufacturer = get_manufacturer_from_mac(mac_address)
                if manufacturer:
                    device_info["manufacturer"] = manufacturer
            
            # 尝试解析主机名
            hostname = get_hostname(ip)
            if hostname:
                device_info["hostname"] = hostname
            
            devices.append(device_info)
        
        return devices
        
    except Exception as e:
        raise RuntimeError(f"获取局域网设备信息时发生错误: {e}")


def get_local_ip() -> Optional[str]:
    """获取本地主机的IP地址"""
    try:
        # 创建一个UDP套接字但不实际连接
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部地址，不需要实际可达
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def get_local_network(local_ip: str) -> Optional[ipaddress.IPv4Network]:
    """根据本地IP地址确定局域网范围"""
    try:
        # 尝试获取子网掩码（Windows系统）
        if platform.system() == "Windows":
            # 使用ipconfig命令获取网络信息
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
            )
            output = result.stdout
            
            # 查找本地IP对应的子网掩码
            pattern = rf"IPv4 Address[\s\S]*?{re.escape(local_ip)}[\s\S]*?Subnet Mask[\s]*:[\s]*(.+?)\r"  
            match = re.search(pattern, output)
            if match:
                subnet_mask = match.group(1)
                network = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
                return network
        else:
            # 非Windows系统使用默认的C类子网
            ip_parts = local_ip.split('.')
            network_cidr = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            network = ipaddress.IPv4Network(network_cidr)
            return network
        
        # 如果无法确定，使用默认的C类子网
        ip_parts = local_ip.split('.')
        network_cidr = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        network = ipaddress.IPv4Network(network_cidr)
        return network
        
    except Exception:
        return None


def ping_host(ip: str) -> bool:
    """Ping指定的IP地址，检查主机是否在线"""
    try:
        # 根据操作系统选择ping命令参数
        if platform.system() == "Windows":
            param = "-n 1 -w 1000"
        else:
            param = "-c 1 -W 1"
        
        # 执行ping命令
        result = subprocess.run(
            ["ping", param, ip],
            capture_output=True,
            text=True,
            shell=True  # 在Windows上需要shell=True来正确处理参数
        )
        
        # 检查ping是否成功
        return result.returncode == 0
        
    except Exception:
        return False


def scan_network(network: ipaddress.IPv4Network, max_workers: int = 100) -> List[str]:
    """使用多线程ping扫描局域网中的所有主机"""
    live_hosts = []
    
    # 排除网络地址和广播地址
    hosts = list(network.hosts())
    
    # 使用线程池并行ping
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有ping任务
        future_to_ip = {executor.submit(ping_host, str(ip)): ip for ip in hosts}
        
        # 收集结果
        for future in future_to_ip:
            ip = future_to_ip[future]
            try:
                if future.result():
                    live_hosts.append(str(ip))
            except Exception:
                pass
    
    return live_hosts


def get_mac_address(ip: str) -> Optional[str]:
    """获取指定IP地址的MAC地址"""
    try:
        if platform.system() == "Windows":
            # 在Windows上使用arp命令
            result = subprocess.run(
                ["arp", "-a", ip],
                capture_output=True,
                text=True
            )
            
            # 解析arp输出
            pattern = rf"{re.escape(ip)}\s+([0-9A-Fa-f:-]+)"
            match = re.search(pattern, result.stdout)
            if match:
                return match.group(1)
        else:
            # 在Linux/Mac上使用arp命令
            result = subprocess.run(
                ["arp", ip],
                capture_output=True,
                text=True
            )
            
            # 解析arp输出
            pattern = r"\s+([0-9A-Fa-f:-]+)"
            match = re.search(pattern, result.stdout)
            if match:
                return match.group(1)
        
        return None
        
    except Exception:
        return None


def get_hostname(ip: str) -> Optional[str]:
    """尝试通过IP地址解析主机名"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return None


def get_manufacturer_from_mac(mac: str) -> Optional[str]:
    """尝试从MAC地址获取设备制造商信息（简化版本）"""
    try:
        # 提取MAC地址的前3个字节（OUI部分）
        mac = mac.replace(":", "").replace("-", "").upper()
        oui = mac[:6]
        
        # 这里可以添加一个简单的OUI到制造商的映射表
        # 注意：这只是一个很小的示例，完整的OUI数据库需要从IEEE获取
        oui_mapping = {
            "005056": "VMware",
            "001C42": "Parallels",
            "00155D": "Microsoft",
            "000C29": "VMware",
            "ACDE48": "Intel",
            "F8E43B": "Apple",
            "4C8B1D": "Apple",
            "B827EB": "Raspberry Pi",
            "00E04C": "Realtek",
            "001B21": "Dell"
        }
        
        return oui_mapping.get(oui)
        
    except Exception:
        return None

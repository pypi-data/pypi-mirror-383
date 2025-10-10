import os

IMG_TYPE = ["jpg", "jpeg", "png"]

def all_files(f_path: str, recursive: bool = False) -> list[str]:
    """列出指定目录下的所有文件名
    
    Args:
        f_path: 要扫描的目录路径
        recursive: 是否递归扫描子目录，默认为False
    
    Returns:
        包含所有文件名的列表
    """
    if not os.path.exists(f_path):
        return []
    if not os.path.isdir(f_path):
        return []
    
    file_names = []
    try:
        if recursive:
            # 递归扫描所有子目录
            for root, _, files in os.walk(f_path):
                for file in files:
                    # 返回相对路径或者仅文件名，这里选择仅文件名
                    file_names.append(file)
        else:
            # 仅扫描当前目录
            for item in os.listdir(f_path):
                item_path = os.path.join(f_path, item)
                if os.path.isfile(item_path):
                    file_names.append(item)
    except PermissionError:
        # 处理权限错误
        pass
    except Exception:
        # 处理其他可能的异常
        pass
    
    return file_names

def all_images(f_path: str, f_ext: list[str], recursive: bool = False) -> list[str]:
    """列出指定目录下的所有指定类型的图片文件
    
    Args:
        f_path: 要扫描的目录路径
        f_ext: 要匹配的文件扩展名列表（不包含点号）
        recursive: 是否递归扫描子目录，默认为False
    
    Returns:
        包含所有匹配文件的列表
    """
    files = all_files(f_path, recursive)
    images: list[str] = []
    if not files:
        return []
    
    # 将扩展名统一转换为小写，确保大小写不敏感
    f_ext_lower = [ext.lower() for ext in f_ext]
    
    for f in files:
        # 获取文件扩展名并转换为小写
        _, ext = os.path.splitext(f)
        ext = ext.lstrip('.').lower()  # 移除点号并转换为小写
        
        if ext in f_ext_lower:
            images.append(f)
    
    return images

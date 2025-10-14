import os
import shutil
from tqdm import tqdm

def copyjindu(source, destination, buffer_size=1024*1024):
    """
    复制文件并显示进度条
    
    参数:
        source (str): 源文件路径
        destination (str): 目标文件路径
        buffer_size (int): 缓冲区大小，默认1MB
    
    返回:
        bool: 复制成功返回True，失败返回False
    """
    try:
        # 检查源文件是否存在
        if not os.path.exists(source):
            raise FileNotFoundError(f"源文件不存在: {source}")
        
        # 获取源文件大小
        total_size = os.path.getsize(source)
        
        # 创建目标目录（如果不存在）
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        # 使用tqdm显示进度条
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            with tqdm(total=total_size, unit='B', unit_scale=True, 
                     desc=f"复制 {os.path.basename(source)}", ncols=80) as pbar:
                while True:
                    buffer = src.read(buffer_size)
                    if not buffer:
                        break
                    dst.write(buffer)
                    pbar.update(len(buffer))
        
        print(f"文件复制完成: {source} -> {destination}")
        return True
        
    except Exception as e:
        print(f"复制失败: {e}")
        return False

# 可选：添加一个不使用tqdm的简化版本作为备选
def copyjindu_simple(source, destination, buffer_size=1024*1024):
    """
    复制文件并显示简单进度（不使用tqdm）
    """
    try:
        if not os.path.exists(source):
            raise FileNotFoundError(f"源文件不存在: {source}")
        
        total_size = os.path.getsize(source)
        copied_size = 0
        
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                buffer = src.read(buffer_size)
                if not buffer:
                    break
                dst.write(buffer)
                copied_size += len(buffer)
                progress = (copied_size / total_size) * 100
                print(f"\r进度: {copied_size}/{total_size} bytes ({progress:.1f}%)", end='', flush=True)
        
        print("\n复制完成!")
        return True
        
    except Exception as e:
        print(f"\n复制失败: {e}")
        return False
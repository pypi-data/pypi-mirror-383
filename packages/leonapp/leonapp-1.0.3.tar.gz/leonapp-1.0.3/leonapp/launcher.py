import os
import sys
import subprocess
from pathlib import Path

def find_leonapp_gui():
    """查找leonapp_gui.py的位置"""
    # 1. 检查当前工作目录
    current_dir = os.getcwd()
    current_path = os.path.join(current_dir, "leonapp_gui.py")
    if os.path.exists(current_path):
        return current_path
    
    # 2. 检查安装目录下的leonapp_data子目录（打包的根目录文件）
    # 获取Python站点包目录
    for site_pkg in sys.path:
        if 'site-packages' in site_pkg:
            data_path = os.path.join(site_pkg, "leonapp_data", "leonapp_gui.py")
            if os.path.exists(data_path):
                return data_path
    
    # 3. 检查用户主目录
    home_dir = str(Path.home())
    home_path = os.path.join(home_dir, "leonapp_gui.py")
    if os.path.exists(home_path):
        return home_path
    
    return None

def main():
    """主函数：启动leonapp_gui.py"""
    script_path = find_leonapp_gui()
    
    if not script_path:
        print("错误：找不到leonapp_gui.py文件", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 运行leonapp_gui.py
        subprocess.run(
            [sys.executable, script_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"运行出错: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
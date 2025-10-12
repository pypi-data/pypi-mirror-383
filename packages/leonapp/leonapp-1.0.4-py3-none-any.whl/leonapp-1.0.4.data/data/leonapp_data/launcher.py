import os
import sys
import subprocess
import site

def find_leonapp_gui():
    """查找leonapp_gui.py文件，优先检查打包的安装目录"""
    # 1. 检查安装包中的leonapp_data目录（最可靠的位置）
    # 获取所有site-packages目录
    site_packages_dirs = site.getsitepackages()
    # 对于用户安装的包，添加用户site-packages目录
    user_site = site.getusersitepackages()
    if user_site not in site_packages_dirs:
        site_packages_dirs.append(user_site)
    
    for sp_dir in site_packages_dirs:
        data_dir = os.path.join(sp_dir, "leonapp_data")
        if os.path.isdir(data_dir):
            # 检查数据目录中是否有目标文件
            target_path = os.path.join(data_dir, "leonapp_gui.py")
            if os.path.exists(target_path):
                return target_path
                
            # 检查数据目录的子目录
            for root, _, files in os.walk(data_dir):
                if "leonapp_gui.py" in files:
                    return os.path.join(root, "leonapp_gui.py")
    
    # 2. 检查当前工作目录及其子目录
    current_dir = os.getcwd()
    for root, _, files in os.walk(current_dir):
        if "leonapp_gui.py" in files:
            return os.path.join(root, "leonapp_gui.py")
    
    # 3. 检查用户主目录及其子目录
    home_dir = os.path.expanduser("~")
    for root, _, files in os.walk(home_dir):
        if "leonapp_gui.py" in files:
            return os.path.join(root, "leonapp_gui.py")
    
    return None

def main():
    """主函数：启动leonapp_gui.py"""
    script_path = find_leonapp_gui()
    
    if not script_path:
        print("错误：找不到leonapp_gui.py文件", file=sys.stderr)
        print("可能的原因：", file=sys.stderr)
        print("1. 安装包可能不完整，请尝试重新安装", file=sys.stderr)
        print("2. 文件可能未被正确打包", file=sys.stderr)
        print("3. 请手动将leonapp_gui.py放在当前目录下", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 打印找到的文件路径（用于调试）
        print(f"找到leonapp_gui.py: {script_path}")
        
        # 运行leonapp_gui.py
        subprocess.run(
            [sys.executable, script_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"运行出错: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
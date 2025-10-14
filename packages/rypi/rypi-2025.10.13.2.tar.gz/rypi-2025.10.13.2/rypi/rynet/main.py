#!/usr/bin/env python
'''
一个网络服务器管理工具, 后端程序: Faskapi + Uvicorn + Nginx + ArangoDB + SeaWeedFS。
'''

VER = r'''
RyNet Version: 2025.8.1.1.0
'''

INFO = r'''
锐网(RyNet): 一个网络服务器管理工具, 后端程序: Faskapi + Uvicorn + Nginx + ArangoDB + SeaWeedFS

更多内容请前往 锐码 官网查阅: admin.rymaa.cn
作者: 锐白
主页: rybby.cn, ry.rymaa.cn
邮箱: rybby@163.com
'''

HELP = r'''
+-------------------------------------------+
|    RyNet: Net Server Management Script    |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi rynet [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -r, --run   run task / 运行指定任务，任务列表如下：

        1    Start Venv / 开启虚拟环境
        2    Stop Venv / 停止虚拟环境
        3    Start Nginx / 开启恩吉克斯
        4    Stop Nginx / 停止恩吉克斯
        5    Start Uvicorn / 开启优维康
        6    Stop Uvicorn / 停止优维康
        7    Start ArangoDB / 开启浪哥(橙子)
        8    Stop ArangoDB / 停止浪哥(橙子)
        9    Start Service / 开启海草
        0    Stop Service / 停止海草
        st    Start Service / 开启所有服务
        sp    Stop Service / 停止所有服务
        ck    Check Service Status / 查看服务状态
        q    Quit / 退出
        ah   Add Host / 添加主机
        dh   Del Host / 删除主机
        lh   List Host / 列出主机
        ef   Edit Config / 编辑配置
        pv   Python Versions / 
        nv   Nginx Versions / 
        av   ArangoDB Versions / 
'''

##############################

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 脚本运行模式的路径修复
pjt_root = None
if __name__ == '__main__' and __package__ is None:
    # 将项目根目录（pjt_rypi/）临时加入 sys.path
    pjt_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, pjt_root)
    # 手动设置包名（包目录: pjt_rypi/rypi/）
    __package__ = 'rypi.rynet'

# 导入依赖
try:  # 相对导入
    from . import conf as rynet_conf
    from .. import comm
except ImportError:
    try:  # 包名导入
        from rypi.rynet import conf as rynet_conf
        from rypi import comm
    except ImportError:  # 绝对导入
        import conf as rynet_conf
        import comm

##############################

def is_linux():
    return sys.platform == "linux" or sys.platform == "linux2"

def is_windows():
    return sys.platform == "win32"

def find_nginx():
    """自动查找 nginx.exe 路径"""
    # 检查环境变量中的路径
    for path in os.environ["PATH"].split(os.pathsep):
        nginx_path = os.path.join(path, "nginx.exe")
        if os.path.isfile(nginx_path):
            return Path(nginx_path).parent
    # 尝试常见安装路径
    for common_path in [
        r"C:\nginx",
        r"C:\Program Files\nginx",
        r"C:\Program Files (x86)\nginx",
        r"D:\www\nginx",
        r"D:\nginx",
        r"D:\Program Files\nginx",
        r"D:\Program Files (x86)\nginx"
    ]:
        nginx_path = os.path.join(common_path, "nginx.exe")
        if os.path.isfile(nginx_path):
            return Path(nginx_path).parent
    raise FileNotFoundError("Not found nginx.exe")

def start_venv():
    try:
        if is_linux():
            cmd = ["source", "rynetenv/bin/activate", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows():
            subprocess.run(["\\rynetenv\\Scripts\\activate"], shell=True, start_new_session=True)
        print("Ok: Virtual environment Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Virtual environment Start Fail: {e}")
        return False

def stop_venv():
    try:
        if is_linux():
            subprocess.run(["deactivate"], shell=True)
        elif is_windows():
            subprocess.run(["\\rynetenv\\Scripts\\deactivate"], shell=True)
        print("Ok: Virtual environment Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Virtual environment Stop Fail: {e}")
        return False

def start_nginx():
    try:
        if is_linux():
            cmd = ["sudo", "systemctl", "start", "nginx", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows():
            original_dir = os.getcwd()  # 保存当前目录
            nginx_dir = find_nginx()
            os.chdir(nginx_dir)
            subprocess.run("start /B nginx.exe > NUL 2>&1", shell=True, start_new_session=True)
            os.chdir(original_dir)
        print("Ok: Nginx Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Nginx Start Fail: {e}")
        return False

def stop_nginx():
    try:
        if is_linux():
            subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
        elif is_windows():
            subprocess.run(["taskkill", "/F", "/T", "/IM", "nginx.exe"], shell=True)
        print("Ok: Nginx Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Nginx Stop Fail: {e}")
        return False

def create_default_config(conf_path):
    """创建默认的nginx配置文件"""
    os.makedirs(os.path.dirname(conf_path), exist_ok=True)
    default_config = """
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    server {
        listen       80;
        server_name  localhost;
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
"""
    with open(conf_path, "w") as f:
        f.write(default_config)

def start_uvi(host: str = "0.0.0.0", port: int = 8000, background: bool = True):
    try:
        if is_linux() and background:
            # 使用 nohup 和 & 在 Linux 后台运行
            cmd = ["sudo", "nohup", "uvicorn", "api:app", "--host", str(host), "--port", str(port), "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows() and background:
            # Windows 使用 start 命令后台运行
            cmd = f'start /B uvicorn api:app --host {host} --port {str(port)} > NUL 2>&1'
            subprocess.run(cmd, shell=True, start_new_session=True)
        else:
            return
        
        print("Ok: Uvicorn Start Success")
        print(f"Uvicorn Started on {host}:{port}" + (" (Background)" if background else ""))
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Uvicorn Start Fail: {e}")
        return False

def stop_uvi():
    try:
        if is_linux():
            subprocess.run(["sudo", "pkill", "-f", "gunicorn"], shell=True)
        elif is_windows():
            subprocess.run(["taskkill", "/f", "/im", "uvicorn.exe"], shell=True)
        else:
            return
        print("Ok: Uvicorn Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Uvicorn Stop Fail: {e}")
        return False

def start_arangodb() -> bool:
    """启动 ArangoDB 服务"""
    try:
        # Linux/macOS (需根据实际路径调整)
        if is_linux():
            cmd = ["sudo", "systemctl", "start", "arangodb", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        # Windows (需确保 ArangoDB 已安装为服务)
        elif is_windows():
            subprocess.run(["net", "start", "ArangoDB"], shell=True, start_new_session=True)
        print("Ok: ArangoDB Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: ArangoDB Start Fail: {e}")
        return False

def stop_arangodb() -> bool:
    """停止 ArangoDB 服务"""
    try:
        # Linux/macOS
        if is_linux():
            subprocess.run(["sudo", "systemctl", "stop", "arangodb"], shell=True)
        # Windows
        elif is_windows():
            subprocess.run(["net", "stop", "ArangoDB"], shell=True)
        print("Ok: ArangoDB Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: ArangoDB Stop Fail: {e}")
        return False

def start_service():
    start_venv()
    start_nginx()
    start_uvi()
    start_arangodb()

def stop_service():
    stop_venv()
    stop_nginx()
    stop_uvi()
    stop_arangodb()

def add_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def del_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def list_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def edit_conf():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def python_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def nginx_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def arangodb_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def run_task(option):
    try:
        if option == '1':
            start_venv()
        elif option == '2':
            stop_venv()
        elif option == '3':
            start_nginx()
        elif option == '4':
            stop_nginx()
        elif option == '5':
            start_uvi()
        elif option == '6':
            stop_uvi()
        elif option == '7':
            start_arangodb()
        elif option == '8':
            stop_arangodb()
        elif option == '9':
            start_service()
        elif option == '0':
            stop_service()
        elif option == 'q':
            return
        elif option == 'ah':
            add_host()
        elif option == 'dh':
            del_host()
        elif option == 'lh':
            list_host()
        elif option == 'ef':
            edit_conf()
        elif option == 'pv':
            python_ver()
        elif option == 'nv':
            nginx_ver()
        elif option == 'av':
            arangodb_ver()
        else:
            print("Invalid option. Please try again.")
    except Exception as e:
        print(f"Error: {str(e)}")

def main(args=None):
    '''
    入口主函数。
    返回: void
    参数列表：
        args (str): 参数列表，通过命令行传入或调用者传入。
    '''

    # 全局选项
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-m', '--module', action='store_true')
    parser.add_argument('-r', '--run')

    # 获取当前目录的所有子模块
    smod = comm.get_modules(__package__)

    # 创建子模块解析器
    subp = parser.add_subparsers(dest='smod', required=False)

    # 定义子模块
    for name, _, _ in smod:
        subp.add_parser(name, add_help=False)

    # 只解析到子模块名称，剩下的参数作为未知参数留给子模块处理
    args, args2 = parser.parse_known_args(args)
    #print(f'args: {args}, args2: {args2}')

    if args.version:
        print(VER)
    elif args.info:
        print(INFO)
    elif args.help:
        print(HELP)

    # 显示子模块
    elif args.module:
        print(f'\n可以在模块名称后加参数(-H)查看该模块的帮助信息。')
        print(f'\n名称前面带横线(-)的是命令模块（目录），否则是辅助模块（脚本 .py 文件）。')
        print(f'\nmodule list:')
        for name, desc, ispkg in smod:
            sub = '-' if ispkg else ' '
            print(f'\n  {sub} {name}: {desc}')

    # 调用子模块
    elif args.smod:
        for name, desc, ispkg in smod:
            if name == args.smod:
                #print(f'name: {name}, args: {args2}')
                comm.run_mod(__package__, name, ispkg, args2)

    elif args.run:
        run_task(args.run)
        
    # 显示帮助
    else:
        print(HELP)

if __name__ == '__main__':
    main()
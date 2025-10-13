#!/usr/bin/env python
'''
锐派(RyPi) 是 锐白 开发的 派神(python) 工具包。
'''

VER = r'''
RyPi Version: 2025.8.13.1.6
'''

INFO = r'''
锐派(RyPi): 是 锐白 开发的 派神(python) 工具包, 包含以下网络工具: 
锐网(RyNet): 一个网络服务器管理工具, 后端程序: Faskapi + Uvicorn + Nginx + ArangoDB + SeaWeedFS
锐通(RyTo): 通用/公用(Util)函数/工具库(Tools)
锐鸥(RyO): 一个网站工具, 包含前端与后端程序, 后端开发语言: 派神(python)
锐代(RyDy): 一个网络数据抓包代理工具
锐辅(RyFu): 一个辅助工具, 可用于执行日常自动任务, 如: 游戏辅助, 广告辅助, 应用辅助
锐爬(RyPa): 一个网络内容爬取工具, 如新闻内容, 电影内容, 电商内容
锐库(RyKu): 一个简易数据库
锐窗(RyWin): 用 派神(python) 开发的 锐派(RyPi) 图形窗口，方便在图形界面系统(PyQt)或终端(Urwid)进行图形可视化操作

更多内容请前往 锐码 官网查阅: rymaa.cn
作者: 锐白
主页: rybby.cn, ry.rymaa.cn
邮箱: rybby@163.com
'''

HELP = r'''
+-------------------------------------------+
|        RyPi: Rybby's Python Tools         |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -m, --module   Show module / 显示子模块
'''

##############################

import os
import sys
import argparse

# 脚本运行模式的路径修复
pjt_root = None
if __name__ == '__main__' and __package__ is None:
    # 将项目根目录（pjt_rypi/）临时加入 sys.path
    pjt_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, pjt_root)
    # 手动设置包名（包目录: pjt_rypi/rypi/）
    __package__ = 'rypi'

# 导入依赖
try:  # 相对导入
    from . import conf
    from . import comm
except ImportError:
    try:  # 包名导入
        from rypi import conf, comm
    except ImportError:  # 绝对导入
        import conf, comm

##############################

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

    # 显示帮助
    else:
        print(HELP)

if __name__ == '__main__':
    main()
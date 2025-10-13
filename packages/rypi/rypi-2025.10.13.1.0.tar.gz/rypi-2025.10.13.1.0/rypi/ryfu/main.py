#!/usr/bin/env python
'''
一个辅助工具, 可用于执行日常自动任务, 如: 游戏辅助, 广告辅助, 应用辅助。
'''

VER = r'''
RyFu Version: 2025.8.1.1.0
'''

INFO = r'''
RyFu: 一个辅助工具, 可用于执行日常自动任务, 如: 游戏辅助, 广告辅助, 应用辅助
'''

HELP = r'''
+-------------------------------------------+
|             RyFu: fuzu script             |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi ryfu [option]

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
    pjt_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, pjt_root)
    # 手动设置包名（包目录: pjt_rypi/rypi/）
    __package__ = 'rypi.ryfu'

# 导入依赖
try:  # 相对导入
    from . import conf as ryfu_conf
    from .. import comm
except ImportError:
    try:  # 包名导入
        from rypi.ryfu import conf as ryfu_conf
        from rypi import comm
    except ImportError:  # 绝对导入
        import conf as ryfu_conf
        import comm

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
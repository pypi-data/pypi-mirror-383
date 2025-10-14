#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快递鸟MCP服务 PyPI发布脚本

使用方法:
    python publish.py --test    # 发布到测试PyPI
    python publish.py          # 发布到正式PyPI
    python publish.py --check   # 仅检查构建
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result


def clean_build():
    """清理构建目录"""
    print("\n=== 清理构建目录 ===")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        if '*' in pattern:
            run_command(f'rmdir /s /q {pattern} 2>nul || echo "目录不存在: {pattern}"', check=False)
        else:
            path = Path(pattern)
            if path.exists():
                run_command(f'rmdir /s /q "{path}"', check=False)


def install_build_tools():
    """安装构建工具"""
    print("\n=== 安装/更新构建工具 ===")
    run_command("pip install --upgrade pip setuptools wheel build twine hatchling")


def build_package():
    """构建包"""
    print("\n=== 构建包 ===")
    run_command("python -m build")


def check_package():
    """检查包的完整性"""
    print("\n=== 检查包 ===")
    run_command("python -m twine check dist/*")


def upload_to_test_pypi():
    """上传到测试PyPI"""
    print("\n=== 上传到测试PyPI ===")
    print("请确保已配置TestPyPI的API token")
    print("配置方法: pip install keyring, 然后设置 TWINE_USERNAME=__token__ 和 TWINE_PASSWORD=<your-token>")
    
    run_command("python -m twine upload --repository testpypi dist/*")
    print("\n测试安装命令:")
    print("pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kdnmcp")


def upload_to_pypi():
    """上传到正式PyPI"""
    print("\n=== 上传到正式PyPI ===")
    print("请确保已配置PyPI的API token")
    print("配置方法: pip install keyring, 然后设置 TWINE_USERNAME=__token__ 和 TWINE_PASSWORD=<your-token>")
    
    confirm = input("确认要发布到正式PyPI吗? (yes/no): ")
    if confirm.lower() != 'yes':
        print("取消发布")
        return
    
    run_command("python -m twine upload dist/*")
    print("\n安装命令:")
    print("pip install kdnmcp")


def check_version():
    """检查版本信息"""
    print("\n=== 版本信息 ===")
    
    # 从pyproject.toml读取版本
    try:
        with open('pyproject.toml', 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version ='):
                    version = line.split('=')[1].strip().strip('"')
                    print(f"当前版本: {version}")
                    break
    except Exception as e:
        print(f"读取版本失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='快递鸟MCP服务 PyPI发布工具')
    parser.add_argument('--test', action='store_true', help='发布到测试PyPI')
    parser.add_argument('--check', action='store_true', help='仅检查构建，不上传')
    parser.add_argument('--clean', action='store_true', help='仅清理构建目录')
    
    args = parser.parse_args()
    
    # 检查是否在项目根目录
    if not Path('pyproject.toml').exists():
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        check_version()
        
        if args.clean:
            clean_build()
            return
        
        # 清理并构建
        clean_build()
        install_build_tools()
        build_package()
        check_package()
        
        if args.check:
            print("\n=== 构建检查完成 ===")
            print("包已成功构建并通过检查，可以进行发布")
            return
        
        # 上传
        if args.test:
            upload_to_test_pypi()
        else:
            upload_to_pypi()
        
        print("\n=== 发布完成 ===")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"发布失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在Linux上运行此脚本前，请先执行以下命令安装依赖：
pip install modelscope python-dotenv
modelscope download --model Qwen/Qwen-Image

注意：
1. 确保项目根目录下存在.env文件，包含MODELSCOPE_TOKEN配置
2. 或者可以取消注释main()函数中的自动安装依赖代码
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def install_dependencies():
    """安装必要的依赖包"""
    packages = ['modelscope', 'python-dotenv']
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"{package}安装成功")
        except subprocess.CalledProcessError as e:
            print(f"安装{package}失败: {e}")
            return False
    
    try:
        subprocess.check_call(['modelscope', 'download', '--model', 'Qwen/Qwen-Image'])
        print("Qwen-Image模型下载成功")
    except subprocess.CalledProcessError as e:
        print(f"下载Qwen-Image模型失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    # 可选：自动安装依赖（取消注释下面的代码）
    # if not install_dependencies():
    #     print("依赖安装失败，请手动安装")
    #     return
    
    # 验证ModelScope token
    from modelscope.hub.api import HubApi
    
    # 从环境变量获取token
    modelscope_token = os.getenv('MODELSCOPE_TOKEN')
    if not modelscope_token:
        print("错误：未找到MODELSCOPE_TOKEN环境变量")
        print("请确保项目根目录下的.env文件包含MODELSCOPE_TOKEN配置")
        return None
    
    api = HubApi()
    try:
        api.login(modelscope_token)
        print("ModelScope token验证成功")
    except Exception as e:
        print(f"ModelScope token验证失败: {e}")
        return None
    
    # 数据集下载
    from modelscope.msdatasets import MsDataset
    
    # 创建数据目录（如果不存在）
    data_dir = './qr-blip3o'
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        ds = MsDataset.load('shichen/qr-blip3o', data_dir=data_dir)
        print(f"数据集加载成功，保存在: {data_dir}")
        return ds
    except Exception as e:
        print(f"数据集加载失败: {e}")
        return None

if __name__ == '__main__':
    dataset = main()
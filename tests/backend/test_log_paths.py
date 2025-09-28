#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志路径是否正确
"""

import os
import sys

def test_app_log_path():
    """测试app.py中的日志路径"""
    print("=== 测试 app.py 日志路径 ===")
    
    # 模拟从backend/app.py计算路径
    app_file = os.path.join('backend', 'app.py')
    log_path = os.path.join(os.path.dirname(os.path.dirname(app_file)), 'logs', 'app.log')
    
    print(f"app.py 位置: {app_file}")
    print(f"计算的日志路径: {log_path}")
    print(f"绝对路径: {os.path.abspath(log_path)}")
    
    if os.path.exists(log_path):
        print("[OK] 日志文件存在")
    else:
        print("[FAIL] 日志文件不存在")
    
    return log_path

def test_log_service_path():
    """测试log_service.py中的日志路径"""
    print("\n=== 测试 log_service.py 日志路径 ===")
    
    # 模拟从backend/services/log_service.py计算路径
    service_file = os.path.join('backend', 'services', 'log_service.py')
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(service_file))), 'logs')
    
    print(f"log_service.py 位置: {service_file}")
    print(f"计算的日志目录: {log_dir}")
    print(f"绝对路径: {os.path.abspath(log_dir)}")
    
    if os.path.exists(log_dir):
        print("[OK] 日志目录存在")
    else:
        print("[FAIL] 日志目录不存在")
    
    return log_dir

def main():
    """主函数"""
    print("日志路径测试")
    print("=" * 50)
    
    app_log_path = test_app_log_path()
    service_log_dir = test_log_service_path()
    
    print("\n=== 路径一致性检查 ===")
    app_log_dir = os.path.dirname(app_log_path)
    
    if os.path.abspath(app_log_dir) == os.path.abspath(service_log_dir):
        print("[OK] 两个路径指向同一目录")
    else:
        print("[FAIL] 路径不一致")
        print(f"  app.py 日志目录: {os.path.abspath(app_log_dir)}")
        print(f"  service 日志目录: {os.path.abspath(service_log_dir)}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == '__main__':
    main()

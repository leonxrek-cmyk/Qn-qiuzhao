#!/usr/bin/env python3
"""
测试修复后的ASR功能
"""
import requests
import json
import base64
import os
import sys

# 添加backend目录到Python路径
sys.path.append('backend')

from services.asr_service import ASRService

def test_backend_asr_service():
    """测试后端ASR服务"""
    print("=== 测试后端ASR服务 ===")
    
    # 创建ASR服务实例
    asr = ASRService()
    
    # 测试获取访问令牌
    print("1. 测试获取访问令牌...")
    token = asr.get_access_token()
    if token:
        print(f"访问令牌获取成功: {token[:20]}...")
    else:
        print("访问令牌获取失败")
        return False
    
    # 创建一个简单的16kHz单声道WAV文件用于测试
    print("\n2. 创建测试WAV文件...")
    test_wav_data = create_test_wav()
    print(f"测试WAV文件创建完成，大小: {len(test_wav_data)} bytes")
    
    # 测试语音识别
    print("\n3. 测试语音识别...")
    result = asr.speech_to_text(test_wav_data, "wav")
    
    if result['success']:
        print(f"语音识别成功: {result}")
    else:
        print(f"语音识别失败: {result}")
        return False
    
    return True

def create_test_wav():
    """创建一个简单的测试WAV文件"""
    import struct
    import math
    
    # WAV文件参数
    sample_rate = 16000
    duration = 1.0  # 1秒
    frequency = 440  # 440Hz的A音
    
    # 生成音频数据
    num_samples = int(sample_rate * duration)
    audio_data = []
    
    for i in range(num_samples):
        # 生成正弦波
        sample = math.sin(2 * math.pi * frequency * i / sample_rate)
        # 转换为16位整数
        sample_int = int(sample * 32767)
        audio_data.append(sample_int)
    
    # 构建WAV文件
    wav_data = bytearray()
    
    # RIFF头部
    wav_data.extend(b'RIFF')
    wav_data.extend(struct.pack('<I', 36 + len(audio_data) * 2))  # 文件大小
    wav_data.extend(b'WAVE')
    
    # fmt chunk
    wav_data.extend(b'fmt ')
    wav_data.extend(struct.pack('<I', 16))  # fmt chunk大小
    wav_data.extend(struct.pack('<H', 1))   # PCM格式
    wav_data.extend(struct.pack('<H', 1))   # 单声道
    wav_data.extend(struct.pack('<I', sample_rate))  # 采样率
    wav_data.extend(struct.pack('<I', sample_rate * 2))  # 字节率
    wav_data.extend(struct.pack('<H', 2))   # 块对齐
    wav_data.extend(struct.pack('<H', 16))  # 位深度
    
    # data chunk
    wav_data.extend(b'data')
    wav_data.extend(struct.pack('<I', len(audio_data) * 2))  # 数据大小
    
    # 音频数据
    for sample in audio_data:
        wav_data.extend(struct.pack('<h', sample))
    
    return bytes(wav_data)

def test_api_endpoint():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    try:
        # 测试后端是否运行
        response = requests.post(
            'http://localhost:5000/api/asr/voice_recognition',
            json={'test': True},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"API端点测试成功: {result}")
            return True
        else:
            print(f"API端点测试失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"API端点测试异常: {e}")
        return False

def main():
    """主函数"""
    print("开始测试修复后的ASR功能\n")
    
    # 测试后端服务
    backend_ok = test_backend_asr_service()
    
    # 测试API端点
    api_ok = test_api_endpoint()
    
    print("\n" + "="*50)
    print("测试结果汇总:")
    print(f"后端ASR服务: {'正常' if backend_ok else '异常'}")
    print(f"API端点: {'正常' if api_ok else '异常'}")
    
    if backend_ok and api_ok:
        print("\n所有测试通过！ASR功能修复成功")
    else:
        print("\n部分测试失败，需要进一步检查")

if __name__ == '__main__':
    main()

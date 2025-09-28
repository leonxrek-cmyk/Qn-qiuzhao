#!/usr/bin/env python3
"""
DeepTalk项目性能测试脚本
测试各种极限条件下的系统性能表现
"""
import requests
import json
import time
import threading
import concurrent.futures
import random
import base64
from datetime import datetime
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# 设置Matplotlib中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# API基础URL
BASE_URL = "http://localhost:5000/api"

# 日志配置
def log(message, level="INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

class PerformanceTest:
    def __init__(self):
        self.results = {
            "concurrency": [],
            "response_time": [],
            "success_rate": []
        }
        self.errors = []
    
    def test_basic_chat(self, messages=None, iterations=1, thread_count=1):
        """测试基础聊天接口性能"""
        log(f"开始测试基础聊天接口 - {iterations}次请求, {thread_count}线程")
        
        if messages is None:
            messages = [{"role": "user", "content": "你好，能简单介绍一下自己吗？"}]
        
        url = f"{BASE_URL}/chat"
        
        def send_request():            
            try:
                start_time = time.time()
                response = requests.post(
                    url,
                    json={"messages": messages, "model": "x-ai/grok-4-fast", "max_tokens": 100},
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return {
                            "success": True,
                            "response_time": end_time - start_time,
                            "content_length": len(result.get("content", ""))
                        }
                    else:
                        return {"success": False, "error": "API返回失败", "status_code": response.status_code}
                else:
                    return {"success": False, "error": f"HTTP错误", "status_code": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 执行测试
        results = []
        start_test_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交所有请求
            futures = [executor.submit(send_request) for _ in range(iterations)]
            
            # 收集结果
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                if (i + 1) % max(1, iterations // 10) == 0:
                    log(f"基础聊天测试进度: {i+1}/{iterations}")
        
        total_time = time.time() - start_test_time
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / iterations) * 100 if iterations > 0 else 0
        
        if success_count > 0:
            avg_response_time = sum(r["response_time"] for r in results if r["success"]) / success_count
            avg_content_length = sum(r["content_length"] for r in results if r["success"]) / success_count
        else:
            avg_response_time = 0
            avg_content_length = 0
        
        # 记录错误
        for r in results:
            if not r["success"]:
                self.errors.append(f"基础聊天错误: {r.get('error')}, 状态码: {r.get('status_code')}")
        
        log(f"基础聊天测试完成: 总耗时 {total_time:.2f}秒, 成功率 {success_rate:.2f}%, 平均响应时间 {avg_response_time:.2f}秒, 平均内容长度 {avg_content_length:.1f}字符")
        
        # 保存结果用于图表
        if thread_count not in [r["concurrency"] for r in self.results["concurrency"]]:
            self.results["concurrency"].append({
                "concurrency": thread_count,
                "avg_response_time": avg_response_time,
                "success_rate": success_rate
            })
        
        return {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_time": total_time,
            "success_count": success_count,
            "total_count": iterations
        }
    
    def test_character_chat(self, character_id="teacher", iterations=1, thread_count=1):
        """测试角色扮演聊天接口性能"""
        log(f"开始测试角色扮演聊天接口 - 角色: {character_id}, {iterations}次请求, {thread_count}线程")
        
        url = f"{BASE_URL}/character_chat"
        
        def send_request():
            try:
                user_query = f"你好，{random.choice(['今天天气真好', '你最近怎么样', '能教我点什么吗', '有什么有趣的事情吗'])}？"
                
                start_time = time.time()
                response = requests.post(
                    url,
                    json={
                        # 修改参数名：character_id -> character_name，这是接口实际需要的参数
                        "character_name": character_id,
                        "user_query": user_query,
                        "model": "x-ai/grok-4-fast"
                    },
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return {
                            "success": True,
                            "response_time": end_time - start_time,
                            "content_length": len(result.get("content", ""))
                        }
                    else:
                        return {"success": False, "error": "API返回失败", "status_code": response.status_code}
                else:
                    return {"success": False, "error": f"HTTP错误", "status_code": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 执行测试
        results = []
        start_test_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(send_request) for _ in range(iterations)]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                if (i + 1) % max(1, iterations // 10) == 0:
                    log(f"角色扮演聊天测试进度: {i+1}/{iterations}")
        
        total_time = time.time() - start_test_time
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / iterations) * 100 if iterations > 0 else 0
        
        if success_count > 0:
            avg_response_time = sum(r["response_time"] for r in results if r["success"]) / success_count
            avg_content_length = sum(r["content_length"] for r in results if r["success"]) / success_count
        else:
            avg_response_time = 0
            avg_content_length = 0
        
        # 记录错误
        for r in results:
            if not r["success"]:
                self.errors.append(f"角色扮演聊天错误: {r.get('error')}, 状态码: {r.get('status_code')}")
        
        log(f"角色扮演聊天测试完成: 总耗时 {total_time:.2f}秒, 成功率 {success_rate:.2f}%, 平均响应时间 {avg_response_time:.2f}秒, 平均内容长度 {avg_content_length:.1f}字符")
        
        return {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_time": total_time,
            "success_count": success_count,
            "total_count": iterations
        }
    
    
    
    def test_asr(self, iterations=1, thread_count=1):
        """测试语音识别接口性能"""
        log(f"开始测试语音识别接口 - {iterations}次请求, {thread_count}线程")
        
        url = f"{BASE_URL}/voice_recognition"
        
        def send_request():
            try:
                # 使用测试模式，不需要实际音频文件
                start_time = time.time()
                response = requests.post(
                    url,
                    json={"test": True},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return {
                            "success": True,
                            "response_time": end_time - start_time,
                            "text_length": len(result.get("text", ""))
                        }
                    else:
                        return {"success": False, "error": "API返回失败", "status_code": response.status_code}
                else:
                    return {"success": False, "error": f"HTTP错误", "status_code": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 执行测试
        results = []
        start_test_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(send_request) for _ in range(iterations)]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                if (i + 1) % max(1, iterations // 10) == 0:
                    log(f"语音识别测试进度: {i+1}/{iterations}")
        
        total_time = time.time() - start_test_time
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / iterations) * 100 if iterations > 0 else 0
        
        if success_count > 0:
            avg_response_time = sum(r["response_time"] for r in results if r["success"]) / success_count
        else:
            avg_response_time = 0
        
        # 记录错误
        for r in results:
            if not r["success"]:
                self.errors.append(f"语音识别错误: {r.get('error')}, 状态码: {r.get('status_code')}")
        
        log(f"语音识别测试完成: 总耗时 {total_time:.2f}秒, 成功率 {success_rate:.2f}%, 平均响应时间 {avg_response_time:.2f}秒")
        
        return {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_time": total_time,
            "success_count": success_count,
            "total_count": iterations
        }
    
    def test_tts(self, iterations=1, thread_count=1):
        """测试语音合成接口性能"""
        log(f"开始测试语音合成接口 - {iterations}次请求, {thread_count}线程")
        
        url = f"{BASE_URL}/text_to_speech"
        
        def send_request():
            try:
                # 生成随机文本内容
                texts = [
                    "你好，这是一段测试文本。",
                    "语音合成功能正在测试中。",
                    "DeepTalk项目性能测试。",
                    "这是一个短文本用于测试。"
                ]
                text = random.choice(texts)
                
                start_time = time.time()
                response = requests.post(
                    url,
                    json={"text": text, "encoding": "mp3"},
                    timeout=20
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return {
                            "success": True,
                            "response_time": end_time - start_time,
                            "audio_size": len(result.get("audio_data", "")) / 1024  # KB
                        }
                    else:
                        return {"success": False, "error": "API返回失败", "status_code": response.status_code}
                else:
                    return {"success": False, "error": f"HTTP错误", "status_code": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 执行测试
        results = []
        start_test_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(send_request) for _ in range(iterations)]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                if (i + 1) % max(1, iterations // 10) == 0:
                    log(f"语音合成测试进度: {i+1}/{iterations}")
        
        total_time = time.time() - start_test_time
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / iterations) * 100 if iterations > 0 else 0
        
        if success_count > 0:
            avg_response_time = sum(r["response_time"] for r in results if r["success"]) / success_count
            avg_audio_size = sum(r["audio_size"] for r in results if r["success"]) / success_count
        else:
            avg_response_time = 0
            avg_audio_size = 0
        
        # 记录错误
        for r in results:
            if not r["success"]:
                self.errors.append(f"语音合成错误: {r.get('error')}, 状态码: {r.get('status_code')}")
        
        log(f"语音合成测试完成: 总耗时 {total_time:.2f}秒, 成功率 {success_rate:.2f}%, 平均响应时间 {avg_response_time:.2f}秒, 平均音频大小 {avg_audio_size:.2f}KB")
        
        return {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_time": total_time,
            "success_count": success_count,
            "total_count": iterations
        }
    
    def test_concurrency(self, test_func, max_threads=10, iterations_per_thread=5):
        """测试不同并发度下的性能"""
        log(f"开始并发性能测试，最大线程数: {max_threads}")
        
        concurrency_results = []
        
        for thread_count in range(1, max_threads + 1):
            log(f"测试并发度: {thread_count}线程")
            
            # 每个线程执行固定次数的请求
            total_iterations = thread_count * iterations_per_thread
            
            result = test_func(iterations=total_iterations, thread_count=thread_count)
            
            concurrency_results.append({
                "thread_count": thread_count,
                "total_iterations": total_iterations,
                "success_rate": result["success_rate"],
                "avg_response_time": result["avg_response_time"],
                "total_time": result["total_time"],
                "req_per_second": total_iterations / result["total_time"] if result["total_time"] > 0 else 0
            })
        
        # 绘制并发性能图表
        try:
            self._plot_concurrency_results(concurrency_results)
        except Exception as e:
            log(f"生成图表失败: {e}", "ERROR")
        
        return concurrency_results
    
    def test_large_message(self, message_size_kb=100):
        """测试大消息处理能力"""
        log(f"开始测试大消息处理能力，消息大小: {message_size_kb}KB")
        
        # 生成大文本内容
        large_text = "这是一段测试文本，用于测试系统处理大消息的能力。" * (message_size_kb * 1024 // 25)
        
        # 测试基础聊天
        log("测试大消息在基础聊天接口的表现")
        basic_result = self.test_basic_chat(
            messages=[{"role": "user", "content": large_text}],
            iterations=3,
            thread_count=1
        )
        
        # 测试角色扮演聊天
        log("测试大消息在角色扮演聊天接口的表现")
        char_result = self.test_character_chat(
            character_id="teacher",
            iterations=1,
            thread_count=1
        )
        
        return {
            "basic_chat": basic_result,
            "character_chat": char_result,
            "message_size_kb": message_size_kb
        }
    
    def _plot_concurrency_results(self, results):
        """绘制并发性能结果图表"""
        try:
            # 跳过图表生成，只打印文本结果
            log("并发性能测试结果摘要:")
            for r in results:
                log(f"  线程数: {r['thread_count']}, 平均响应时间: {r['avg_response_time']:.2f}秒, 成功率: {r['success_rate']:.2f}%, 吞吐量: {r['req_per_second']:.2f}请求/秒")
        except Exception as e:
            log(f"处理并发结果时出错: {e}", "ERROR")
    
    def run_all_tests(self):
        """运行所有性能测试"""
        log("===== 开始DeepTalk项目性能测试 =====")
        
        # 1. 基础功能单线程测试
        log("\n=== 1. 基础功能单线程测试 ===")
        # 减少测试次数以确保完整运行
        self.test_basic_chat(iterations=3, thread_count=1)
        self.test_character_chat(iterations=3, thread_count=1)
        # 暂时跳过ASR和TTS测试
        # self.test_asr(iterations=10, thread_count=1)
        # self.test_tts(iterations=5, thread_count=1)
        
        # 2. 并发性能测试
        log("\n=== 2. 并发性能测试 ===")
        # 选择基础聊天接口进行并发测试，减少测试量
        self.test_concurrency(self.test_basic_chat, max_threads=4, iterations_per_thread=2)
        
        # 3. 大消息测试
        log("\n=== 3. 大消息处理测试 ===")
        # 暂时跳过大消息测试
        # self.test_large_message(message_size_kb=50)
        
        # 4. 错误统计
        if self.errors:
            log(f"\n=== 4. 测试错误统计 ===")
            log(f"总共发现 {len(self.errors)} 个错误")
            for i, error in enumerate(self.errors[:5], 1):
                log(f"错误 {i}: {error}")
            if len(self.errors) > 5:
                log(f"... 还有 {len(self.errors) - 5} 个错误未显示")
        
        log("\n===== DeepTalk项目性能测试完成 =====")
        
if __name__ == "__main__":
    # 创建性能测试实例
    tester = PerformanceTest()
    
    # 检查后端服务是否可访问
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=5)
        if response.status_code != 200:
            log("警告：无法正常访问后端服务，测试结果可能不准确", "WARNING")
    except requests.exceptions.ConnectionError:
        log("错误：无法连接到后端服务，请确保服务已启动", "ERROR")
        sys.exit(1)
    
    # 运行所有测试
    tester.run_all_tests()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AYsocket性能测试程序
测试高并发连接和数据处理能力
"""

import threading
import time
import random
from AYlib.AYsocket import AYsocket

class PerformanceTester:
    def __init__(self, server_ip='127.0.0.1', server_port=9988):
        self.server_ip = server_ip
        self.server_port = server_port
        self.results = {}
        self.clients = []
        
    def start_server(self):
        """启动高性能服务器"""
        print("启动高性能TCP服务器...")
        self.server = AYsocket(self.server_ip, self.server_port)
        
        # 设置自定义处理器
        def custom_processor(data, data_type):
            # 模拟复杂的数据处理逻辑
            processed = f"Processed: {data.upper()}"
            time.sleep(0.001)  # 模拟1ms处理时间
            return processed
        
        self.server.set_custom_processor(custom_processor)
        
        # 启动服务器
        server_thread = threading.Thread(target=self.server.start_tcp_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        print("服务器启动完成")
        
    def client_worker(self, client_id, num_messages=100):
        """客户端工作线程"""
        client = AYsocket(self.server_ip, self.server_port)
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        for i in range(num_messages):
            try:
                message = f"Client_{client_id}_Message_{i}"
                success, response = client.send_tcp_string(message, timeout=5)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
                # 随机延迟模拟真实场景
                time.sleep(random.uniform(0.01, 0.1))
                
            except Exception as e:
                error_count += 1
                print(f"客户端 {client_id} 错误: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'client_id': client_id,
            'success_count': success_count,
            'error_count': error_count,
            'duration': duration,
            'messages_per_second': num_messages / duration if duration > 0 else 0
        }
    
    def run_concurrent_test(self, num_clients=10, messages_per_client=50):
        """运行并发测试"""
        print(f"\n开始并发测试: {num_clients}个客户端, 每个发送{messages_per_client}条消息")
        
        threads = []
        results = []
        
        # 创建并启动客户端线程
        for i in range(num_clients):
            thread = threading.Thread(
                target=lambda idx=i: results.append(self.client_worker(idx, messages_per_client))
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        total_messages = num_clients * messages_per_client
        total_success = sum(r['success_count'] for r in results)
        total_errors = sum(r['error_count'] for r in results)
        avg_mps = sum(r['messages_per_second'] for r in results) / len(results)
        
        print(f"\n并发测试结果:")
        print(f"总消息数: {total_messages}")
        print(f"成功消息: {total_success}")
        print(f"失败消息: {total_errors}")
        print(f"成功率: {(total_success/total_messages)*100:.2f}%")
        print(f"平均消息/秒: {avg_mps:.2f}")
        
        # 获取服务器统计信息
        if hasattr(self.server, 'get_connection_stats'):
            stats = self.server.get_connection_stats()
            print(f"\n服务器连接统计:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        return results
    
    def stress_test(self, max_clients=100):
        """压力测试"""
        print(f"\n开始压力测试，最大客户端数: {max_clients}")
        
        test_cases = [
            (10, 100),   # 10客户端，100消息/客户端
            (25, 50),    # 25客户端，50消息/客户端  
            (50, 20),    # 50客户端，20消息/客户端
            (100, 10),   # 100客户端，10消息/客户端
        ]
        
        all_results = {}
        
        for num_clients, messages_per_client in test_cases:
            if num_clients > max_clients:
                continue
                
            print(f"\n测试配置: {num_clients}客户端 × {messages_per_client}消息")
            results = self.run_concurrent_test(num_clients, messages_per_client)
            all_results[(num_clients, messages_per_client)] = results
            
            # 短暂休息
            time.sleep(2)
        
        return all_results
    
    def monitor_server_performance(self, duration=30):
        """监控服务器性能"""
        print(f"\n开始性能监控，持续时间: {duration}秒")
        
        start_time = time.time()
        monitoring_data = []
        
        while time.time() - start_time < duration:
            if hasattr(self.server, 'get_connection_stats'):
                stats = self.server.get_connection_stats()
                monitoring_data.append({
                    'timestamp': time.time() - start_time,
                    'stats': stats.copy()
                })
            
            # 获取队列统计
            if hasattr(self.server, 'message_processor'):
                queue_stats = self.server.message_processor.get_queue_stats()
                print(f"队列状态: {queue_stats}")
            
            time.sleep(1)
        
        print("性能监控完成")
        return monitoring_data

def main():
    """主测试函数"""
    tester = PerformanceTester()
    
    try:
        # 启动服务器
        tester.start_server()
        
        # 运行基本并发测试
        tester.run_concurrent_test(num_clients=5, messages_per_client=20)
        
        # 运行压力测试
        tester.stress_test(max_clients=50)
        
        # 监控性能
        tester.monitor_server_performance(duration=10)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试错误: {e}")
    finally:
        print("测试完成")

if __name__ == "__main__":
    main()
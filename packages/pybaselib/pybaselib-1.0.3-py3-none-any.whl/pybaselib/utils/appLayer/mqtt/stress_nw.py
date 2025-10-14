# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/10/13 13:06
# @Version: 3.0 Optimized for High Concurrency

import asyncio
import json
import math
import time
import ssl
from gmqtt import Client as MQTTClient
import sr_pro_pb2
# OPTIMIZATION 1: 导入我们修改后的异步HTTP客户端
from pybaselib.utils.appLayer.http import AsyncHttp2Client

# --- 1. 测试参数配置 ---
# ==============================================================================
TARGET_TOTAL_CLIENTS = 2000  # 目标要上线的设备总数
CONCURRENT_WORKERS = 1000  # 并发Worker数量 (理论上的并发能力)

# OPTIMIZATION 2: 引入信号量来精细控制并发连接数
# 这个值是关键！它限制了“同一时刻”到底有多少个连接请求在发生。
# 1000个Worker不代表1000个并发连接。这个值才代表。
# 建议从 100-200 开始测试，根据服务器和客户端性能调整。
MAX_CONCURRENT_CONNECTIONS = 200

RETRY_ATTEMPTS = 5  # 单个设备最大重试次数
RETRY_DELAY = 1  # 每次重试前的等待时间(秒)

# MQTT 和 API 配置
EMQX_HOST = "192.168.158.69"
EMQX_PORT = 8883
API_BASE_URL = f"https://{EMQX_HOST}:18443"
API_AUTH_TOKEN = "8gMsKuDOC9g3neUggAIEgOmxrSLPfDMCGn3Ce2VCPvjdWJuDdnsiMxOUWktnuTrZ"


# ==============================================================================


class TestStats:
    """用于线程安全地记录测试统计数据"""

    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.lock = asyncio.Lock()

    async def add_success(self):
        async with self.lock:
            self.success_count += 1

    async def add_failure(self):
        async with self.lock:
            self.failure_count += 1


# --- 2. 核心业务逻辑 (从您的代码中整合和优化) ---

class ApiClient:
    """封装了获取设备ID的API操作 (完全异步)"""

    def __init__(self):
        # OPTIMIZATION 1: 使用异步客户端
        self.httpClient = AsyncHttp2Client(API_BASE_URL, headers={"Authorization": API_AUTH_TOKEN})

    # OPTIMIZATION 1: 所有方法都改为 async def
    async def get_assets_count(self, domain_id="68d3f0ad7b49fd00124c6330", where={'model': "ssslc"}):
        uri = f"/api/core/domains/{domain_id}/assets/count"
        params = {'where': json.dumps(where)}
        rs = await self.httpClient.get(uri, params=params)
        count = rs.get('count')
        print(f"API: Found {count} total assets.")
        return count

    async def get_assets_info(self, domain_id="68d3f0ad7b49fd00124c6330", limit=1000,
                              offset=0, where={'model': "ssslc"}):
        uri = f"/api/core/domains/{domain_id}/assets"
        params = {'filter': json.dumps({
            'limit': limit,
            'offset': offset,
            'where': where,
            'order': 'name asc'
        })}
        rs = await self.httpClient.get(uri, params=params)
        return rs

    async def get_asset_id_list(self, domain_id="68d3f0ad7b49fd00124c6330", where={'model': "ssslc"}, total=50000):
        counts = await self.get_assets_count(domain_id=domain_id, where=where)
        if total > counts:
            raise Exception("请求的设备数量大于实际设备数量")

        endCount = math.ceil(total / 1000)
        assert_id_list = []

        # 创建一个异步任务列表来并行获取设备信息
        tasks = []
        for i in range(endCount):
            offset = i * 1000
            # 如果是最后一页，调整limit
            limit = min(1000, total - offset)
            if limit <= 0: break
            tasks.append(self.get_assets_info(offset=offset, limit=limit, domain_id=domain_id, where=where))

        print(f"Fetching {total} device IDs in {len(tasks)} parallel API calls...")
        # 并发执行所有API请求
        results = await asyncio.gather(*tasks)

        for assert_infos in results:
            for assert_info in assert_infos:
                assert_id = assert_info.get("id")
                if assert_id:
                    assert_id_list.append(assert_id)

        # 确保我们不会超过请求的总数
        return assert_id_list[:total]


async def connect_publish_disconnect(device_id: str, stats: TestStats, ssl_context: ssl.SSLContext,
                                     semaphore: asyncio.Semaphore):
    """
    处理单个设备的核心函数：连接 -> 发送 -> 断开，并包含重试逻辑
    """
    # OPTIMIZATION 2: 在进入核心逻辑前，首先要获取信号量
    async with semaphore:
        for attempt in range(RETRY_ATTEMPTS):
            client = None
            try:
                client = MQTTClient(device_id)
                client.set_config({'keepalive': 60})

                await asyncio.wait_for(
                    client.connect(EMQX_HOST, EMQX_PORT, ssl=ssl_context),
                    timeout=10
                )

                son = sr_pro_pb2.SRMQTTOnlineStatus()
                son.status = 1
                son.parent = device_id
                payload = son.SerializeToString()
                topic = f"notify/status/ssslc/device-common:online-status/{device_id}"
                client.publish(topic, payload=payload, qos=0)

                await asyncio.wait_for(client.disconnect(), timeout=5)

                await stats.add_success()
                return

            except Exception as e:
                # 减少打印，只在最后一次失败时打印
                if attempt >= RETRY_ATTEMPTS - 1:
                    print(f"❌ [{device_id}] All attempts failed. Final error: {e}")

                if client and client.is_connected():
                    try:
                        await client.disconnect()
                    except:
                        pass

                if attempt < RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    await stats.add_failure()
                    return


# --- 3. 压测调度与执行 ---

async def worker(name: str, queue: asyncio.Queue, stats: TestStats, ssl_context: ssl.SSLContext,
                 semaphore: asyncio.Semaphore):
    """
    消费者Worker，不断从队列中取出device_id并处理
    """
    # print(f"[{name}] 启动...") # 在大量worker时，这条打印意义不大
    while True:
        try:
            device_id = await queue.get()
            await connect_publish_disconnect(device_id, stats, ssl_context, semaphore)
            queue.task_done()
        except asyncio.CancelledError:
            # print(f"[{name}] 被取消.")
            break


async def main():
    """压测主函数"""
    print("--- 开始高并发压力测试 ---")
    print(f"目标设备数: {TARGET_TOTAL_CLIENTS}")
    print(f"Worker(协程)数: {CONCURRENT_WORKERS}")
    print(f"实际并发连接数 (通过信号量控制): {MAX_CONCURRENT_CONNECTIONS}")
    print("--------------------------")

    stats = TestStats()
    task_queue = asyncio.Queue()
    api_client = ApiClient()

    # OPTIMIZATION 3: 只创建一次SSLContext
    print("Creating reusable SSL context...")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # 1. 生产者：异步获取所有device_id并放入队列
    print("Asynchronously fetching all device IDs from API...")
    try:
        all_devices = await api_client.get_asset_id_list(total=TARGET_TOTAL_CLIENTS)
        await api_client.httpClient.aclose()  # 优雅地关闭HTTP客户端
    except Exception as e:
        print(f"获取设备ID失败，测试中止: {e}")
        return

    if not all_devices:
        print("未能获取到任何设备ID，测试中止。")
        return

    print(f"成功获取 {len(all_devices)} 个设备ID，开始入队...")
    for device_id in all_devices:
        task_queue.put_nowait(device_id)

    # 2. 消费者：创建信号量和Worker
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONNECTIONS)
    workers = [
        asyncio.create_task(worker(f"Worker-{i}", task_queue, stats, ssl_context, semaphore))
        for i in range(CONCURRENT_WORKERS)
    ]

    start_time = time.time()
    print("\n>>> 所有任务已入队，Worker开始处理，压力测试开始...")

    # 3. 等待队列中所有任务被处理完毕
    await task_queue.join()

    end_time = time.time()
    total_time = end_time - start_time

    # 4. 所有任务完成，取消Worker任务
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    # 5. 打印最终的测试报告
    print("\n--- 测试完成 ---")
    print("--- 测试结果报告 ---")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"成功上线设备数: {stats.success_count}")
    print(f"失败设备数: {stats.failure_count}")

    if total_time > 0:
        actual_rate = stats.success_count / total_time
        print(f"实际平均上线速率: {actual_rate:.2f} 个/秒")

    success_percentage = (stats.success_count / len(all_devices)) * 100 if all_devices else 0
    print(f"连接成功率: {success_percentage:.2f}%")
    print("------------------")


if __name__ == '__main__':
    # 注意：在Linux上运行高并发测试前，请确保已调整文件描述符限制 (ulimit -n)
    # 例如: ulimit -n 65535
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断。")
# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/8/11 13:36

from gmqtt import Client as MQTTClient
import sr_pro_pb2
import uuid
import ssl
import asyncio


async def mqtt_connect_test(mqtt_domain, mqtt_port):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    client_id = f"client-{uuid.uuid4()}"

    client = MQTTClient(client_id)
    client.set_config({'keepalive': 360})
    # client.set_config({'version': 5})
    try:
        await client.connect(mqtt_domain, mqtt_port, ssl=ssl_context)
        return client
    except Exception as e:
        print(f"[{client_id}] 连接失败: {e}")
        return None


async def send_msg(payload, Topic, mqtt_domain="192.168.158.69", mqtt_port=8883):
    client = await mqtt_connect_test(mqtt_domain, mqtt_port)
    # 连接并发布消息
    if client:
        client.publish(Topic, payload=payload, qos=0)
        print(f"消息已发布 {Topic}")


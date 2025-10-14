# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/8/6 09:55

from gmqtt import Client as MQTTClient
import sr_pro_pb2
import uuid
import ssl
import asyncio

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

mqtt_domain = "192.168.158.69"
mqtt_port = 8883
TEST_DURATION = 10  # 秒数
MAX_PRINT = 10  # 打印前10个连接耗时用于观察
TOPIC = "notify/status/ssslc/device-common:online-status/{terminal_id}"
MESSAGES_PER_CLIENT = 1


async def mqtt_connect_test(client_id):
    client = MQTTClient(client_id)
    client.set_config({'keepalive': 360})
    # client.set_config({'version': 5})
    await client.connect(mqtt_domain, mqtt_port, ssl=ssl_context)

    return client

cid = f"client-{uuid.uuid4()}"
# client = mqtt_connect_test(cid)

son = sr_pro_pb2.SRMQTTOnlineStatus()
son.status = 1
son.parent = "{terminal_id}".format(terminal_id="00002CD26BC148BD")
Topic = TOPIC.format(terminal_id="00002CD26BC148BD")

# protobuf_bytes = son.SerializeToString()
# client.publish(Topic, payload=protobuf_bytes, qos=0)

async def main():
    cid = f"client-{uuid.uuid4()}"
    client = await mqtt_connect_test(cid)
    # 构造 protobuf 消息
    son = sr_pro_pb2.SRMQTTOnlineStatus()
    son.status = 1
    son.parent = "{terminal_id}".format(terminal_id="00002CD26BC148BD")

    # 序列化为二进制
    payload = son.SerializeToString()

    # 连接并发布消息
    client.publish(Topic, payload=payload, qos=0)
    print("消息已发布")

    # await asyncio.sleep(2)
    # await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

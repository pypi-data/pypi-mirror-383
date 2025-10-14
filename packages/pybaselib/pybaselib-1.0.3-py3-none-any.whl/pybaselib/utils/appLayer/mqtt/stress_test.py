# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/10/10 13:06
import json
import math
import asyncio
import sr_pro_pb2
import httpx
from pybaselib.utils.appLayer.http import Http2Client
from b import mqtt_connect_test

class StressTest():
    def __init__(self, base_url="https://192.168.158.69:18443", already_url="https://192.168.31.37:18443"):
        self.base_url = base_url
        self.httpClient = Http2Client(base_url,
                                      headers={
                                          "Authorization": "8gMsKuDOC9g3neUggAIEgOmxrSLPfDMCGn3Ce2VCPvjdWJuDdnsiMxOUWktnuTrZ"})

    async def get_assets_count(self, domain_id="68d3f0ad7b49fd00124c6330", where={'model': "ssslc"}):
        """
        获取设备总数
        :param domain_id:
        :return:
        """
        uri = f"/api/core/domains/{domain_id}/assets/count"
        params = {'where': json.dumps(where)}
        # rs = self.already_httpClient.get(uri, params=params)
        rs = self.httpClient.get(uri, params=params)
        count = rs.get('count')
        print(count)
        return count

    async def get_assets_info(self, domain_id="68d3f0ad7b49fd00124c6330", limit=1000,
                              offset=0, where={'model': "ssslc"}):
        """
        获取资产信息
        :param domain_id:
        :param model:
        :return:
        """
        uri = f"/api/core/domains/{domain_id}/assets"
        params = {'filter': json.dumps(
            {'limit': limit,
             'offset': offset,
             'where': where,
             # 'order': "createTime asc"
             # 'order': "id desc"
             'order': 'name asc'
             })}
        # rs = self.already_httpClient.get(uri, params=params)
        rs = self.httpClient.get(uri, params=params)
        # print(rs)
        return rs


    async def get_asset_id(self,domain_id="68d3f0ad7b49fd00124c6330", where={'model': "ssslc"}, total=50000):
        counts = await self.get_assets_count(domain_id=domain_id, where=where)
        if total>counts:
            raise Exception("收集设备数量大于实际设备数量")
        endCount = math.ceil(total / 1000)
        offset = 0
        assert_id_list = []
        for loop in range(1, endCount + 1):
            print(loop)
            assert_infos = await self.get_assets_info(offset=offset, domain_id=domain_id, where=where)
            for assert_info in assert_infos:
                assert_id = assert_info.get("id")
                assert_id_list.append(assert_id)
            offset += 1000

        return assert_id_list


    async def notify_status_model(self, client, deviceId, online_status=1, model="ssslc"):
        # 构造 protobuf 消息
        son = sr_pro_pb2.SRMQTTOnlineStatus()
        son.status = online_status
        son.parent = "{terminal_id}".format(terminal_id=deviceId)

        # 序列化为二进制
        payload = son.SerializeToString()

        topic = f"notify/status/{model}/device-common:online-status/{deviceId}"
        client.publish(topic, payload=payload, qos=0)
        await client.disconnect()

st = StressTest()
DEVICE_COUNT = 60000
BATCH_SIZE = 2400

async def handle_device(device_id):
    client = await mqtt_connect_test("192.168.158.69",8883)
    if client:
        await st.notify_status_model(client, device_id)

async def main():
    all_devices = await st.get_asset_id(total=60000)

    for i in range(0, DEVICE_COUNT, BATCH_SIZE):
        batch = all_devices[i:i+BATCH_SIZE]
        print(f"\n>>> 启动第 {i//BATCH_SIZE + 1} 批，共 {len(batch)} 个连接")

        tasks = [handle_device(device_id) for device_id in batch]
        await asyncio.gather(*tasks)
        # await asyncio.sleep(0.002)  # 批次间隔，防止资源耗尽



if __name__ == '__main__':
    # st = StressTest()
    # print(asyncio.run(st.get_asset_id()))

    # asyncio.run(handle_device("00004080E119356E"))

    asyncio.run(main())

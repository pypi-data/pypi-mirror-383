# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/8/11 13:08
import sr_pro_pb2
import asyncio
from b import send_msg
from datetime import datetime


def notify_status_base(model, status_para, deviceId, payload, status_type="device-common"):
    """
    发送在线状态
    :return: 
    """
    topic = f"notify/status/{model}/{status_type}:{status_para}/{deviceId}"
    asyncio.run(send_msg(payload, topic))


def notify_alert_base(model, alert_type, alert_para, deviceId, value, threshold):
    """
    发送告警通知
    :return:
    """
    topic = f"notify/alert/{model}/{alert_type}:{alert_para}/{deviceId}"

    son = sr_pro_pb2.SRMQTTDeviceAlert()
    son.status = 1
    son.value = value
    son.threshold = threshold
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    son.timestamp = time_str
    # 序列化为二进制
    payload = son.SerializeToString()

    asyncio.run(send_msg(payload, topic))

def notify_status_ssgw(deviceId, online_status=1):
    # 构造 protobuf 消息
    son = sr_pro_pb2.SRMQTTOnlineStatus()
    son.status = online_status
    son.parent = "{terminal_id}".format(terminal_id=deviceId)

    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("ssgw", "online-status", deviceId, payload)
    # notify_status_base("ssslc", "online-status", deviceId, payload)

def notify_status_model(model, deviceId, online_status=1):
    # 构造 protobuf 消息
    son = sr_pro_pb2.SRMQTTOnlineStatus()
    son.status = online_status
    son.parent = "{terminal_id}".format(terminal_id=deviceId)

    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base(model, "online-status", deviceId, payload)

def notify_status_sssap(deviceId, online_status=1):
    """
    上报传感器在线
    :param deviceId:
    :param online_status:
    :return:
    """
    # 构造 protobuf 消息
    son = sr_pro_pb2.SRMQTTOnlineStatus()
    son.status = online_status
    son.parent = "{terminal_id}".format(terminal_id=deviceId)

    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "online-status", deviceId, payload)

def notify_switch_status_base(model, deviceId, value):
    """
    发送在线状态
    :return:
    """
    topic = f"notify/status/{model}/device-sensor:switch-status/{deviceId}"
    son = sr_pro_pb2.SRMQTTSwitchStatus()
    son.param = value
    # 序列化为二进制
    payload = son.SerializeToString()
    asyncio.run(send_msg(payload, topic))

def switch_sstppl(deviceId, value):
    """
    开关供电回路
    :return:
    """
    # notify_switch_status_base("sstppl", deviceId, value)
    notify_switch_status_base("sslamp", deviceId, value)





def notify_alert_sssap_current_leakage_alarm(deviceId):
    """
    漏电故障上报
    :param deviceId:
    :return:
    """
    notify_alert_base("sssap", "device-sensor", "current-leakage-alarm", deviceId, "50", "100")


def notify_alert_sssap_cable_theft_alarm(deviceId):
    """
    电缆被盗故障上报
    :param deviceId:
    :return:
    """
    notify_alert_base("sssap", "device-sensor", "cable-theft-alarm", deviceId, "0", "100")

def notify_alert_water_flooding_alert(deviceId):
    """
    水浸上报 8403185720432808_1605001 water-flooding-alert
    :return:
    """
    notify_alert_base("sssap", "device-sensor", "water-flooding-alert", deviceId, "50", "100")

def notify_cellular(deviceId):
    """
    上报网络信息
    message Cellular {
      string imei = 1;         // 设备识别码
      string imsi = 2;         // 用户识别码
      string iccid = 3;        // SIM卡识别码
      string operator = 4;     // 运营商名称
      string net_type = 5;     // 网络类型
    }
    :param deviceId:
    :return:
    """
    son = sr_pro_pb2.Cellular()
    son.imei = "783203921309123"
    son.imsi = "987654321234563"
    son.iccid = "380123453450923"
    son.operator = "DACC"
    son.net_type = "**"

    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "cellular", deviceId, payload)

def notify_cellular_status(deviceId):
    """
    上报网络状态
    /*
     * Common:Data:CellularStatus
     * 蜂窝式终端设备状态
     */
    message CellularStatus {
      uint32 module = 1;      // 模块状态 0：正常，1：异常
      uint32 sim = 2;         // SIM卡状态 0：存在，1：不存在
      int32 rssi = 3;         // 接收信号强度
    }
    :param deviceId:
    :return:
    """
    son = sr_pro_pb2.CellularStatus()
    son.module = 1
    son.sim = 1
    son.rssi = 75
    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "cellular-status", deviceId, payload)


def notify_battery_status(deviceId):
    """
    上报电池状态
    message BatteryStatus {
      ChargeStatus status = 1;            // 充电状态 1 充电中 2 放电中 3 充电截止 4 放电截止  其他未知
      float current = 2;                  // 电流 (单位: A) ，充电为正值，放电为负值, 未知和充/放电截止时，为0
      float voltage = 3;                  // 电压 (单位: V), 电池电压
      uint32 soc = 4;                     // State of Charge，它表示当前电池剩余电量占满充电容量的百分比
      float temperature = 5;              // 电池温度(单位：℃)
    }
    :param deviceId:
    :return:
    """

    son = sr_pro_pb2.BatteryStatus()
    son.status = 3
    son.current = 13.4509
    son.voltage = 5.2345
    son.soc = 100
    son.temperature = 34.26
    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "battery-status", deviceId, payload)

def notify_power_in_status(deviceId):
    """
    上报电能状态
    // 设备的供电输入状态
    message PowerInStatus {
      bool has_power = 1;       // 当前是否通电  0 无电
      float voltage = 2;        // 当前输入电压值 (单位: V)
    }
    :param deviceId:
    :return:
    """
    son = sr_pro_pb2.PowerInStatus()
    son.has_power = 1
    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "power-in-status", deviceId, payload)


def notify_roadSurface(deviceId):
    """
    // 路面状态
    // 参考来源《中国气象局综合观测司-公路交通气象观测站功能规格需求书》
    message RoadSurfaceCondition {
      uint32 status = 1;                  // 路面状态编码。0：未知; 11：干燥; 12：潮湿; 13：积水; 14：积雪; 15：结冰; 16:结霜; 17: 有融雪剂; 99：其他
      double thickness = 2;               // 厚度(mm),与路面状态对应。13：表示积水厚度；14：表示积雪厚度；15：表示冰层厚度；其他为0
      double surface_temperature = 3;     // 路面温度 0.1ºC
      // double roadbed_temperature = 4;     // 路基温度 0.1%RH
    }

    :param deviceId:
    :return:
    """
    son = sr_pro_pb2.RoadSurfaceCondition()
    son.status = 14
    son.thickness = 15
    son.surface_temperature = 0
    # 序列化为二进制
    payload = son.SerializeToString()
    notify_status_base("sssap", "road-surface-condition", deviceId, payload, status_type="device-sensor")

if __name__ == "__main__":
    # 配电柜在线
    # notify_status_ssgw("000034A48CCFD609")
    # notify_status_ssgw("00004080E119356E")
    # notify_status_ssgw("8384023780129380")
    notify_status_model("ssslc", "00004080E119356E")

    # switch_sstppl("000034A48CCFD609_0406003", 1)  #k
    # switch_sstppl("00004080E119356E_0000001", 1)

    # notify_alert_sssap_current_leakage_alarm("3401000000003401_1405002")
    # notify_alert_sssap_current_leakage_alarm("00006A2D1E13A9D4_2303011")
    # notify_alert_sssap_current_leakage_alarm("3285784508013943_1405001")

    # 电缆故障上报
    # notify_alert_sssap_cable_theft_alarm("3445225245676432")
    # notify_alert_sssap_cable_theft_alarm("7830183710231893")  #电缆被盗2

    # notify_alert_water_flooding_alert("000034A48CCFD609_0406004")

    #上报传感器在线
    # notify_status_sssap("00006A2D1E13A9D4_2303011")
    # notify_status_sssap("3445225245676432")

    # 上报网络信息
    # notify_cellular("3445225245676432")

    # 上报网络状态
    # notify_cellular_status("3445225245676432")

    # 上报电池状态
    # notify_battery_status("3445225245676432")

    # 上报电能状态
    # notify_power_in_status("3445225245676432")

    # 上报路面状态
    # notify_roadSurface("00006A2D1E13A9D4_2303011")
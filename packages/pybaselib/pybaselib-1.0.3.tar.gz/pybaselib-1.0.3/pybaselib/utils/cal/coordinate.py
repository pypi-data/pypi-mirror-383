# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/9/25 10:37

import math

def offset_bd09_coordinate(lat, lng, offset_north_meters, offset_east_meters):
    """
    平移指定的BD-09坐标点。

    参数:
    lat (float): 原始纬度
    lng (float): 原始经度
    offset_north_meters (float): 向北平移的米数 (向南为负数)
    offset_east_meters (float): 向东平移的米数 (向西为负数)

    返回:
    (float, float): 包含新纬度和新经度的元组
    """
    # 地球平均半径，单位：米
    earth_radius = 6371000.0

    # 1. 计算纬度偏移
    # 纬度上每度的距离是固定的
    meters_per_degree_lat = (2 * math.pi * earth_radius) / 360.0
    lat_offset_degrees = offset_north_meters / meters_per_degree_lat
    new_lat = lat + lat_offset_degrees

    # 2. 计算经度偏移
    # 经度上每度的距离取决于当前纬度
    # 首先将原始纬度从角度转换为弧度
    lat_rad = math.radians(lat)
    meters_per_degree_lng = (2 * math.pi * earth_radius * math.cos(lat_rad)) / 360.0
    lng_offset_degrees = offset_east_meters / meters_per_degree_lng
    new_lng = lng + lng_offset_degrees

    return new_lat, new_lng


if __name__ == '__main__':
    # --- 使用您的数据进行示例 ---

    # 原始坐标点 (来自您的第一条数据)
    original_lat = 31.87186547611894
    original_lng = 120.62165278832789

    # 平移距离：向北50米，向东100米
    offset_n = 50
    offset_e = 100

    # 调用函数计算新坐标
    new_latitude, new_longitude = offset_bd09_coordinate(original_lat, original_lng, offset_n, offset_e)

    print(f"原始坐标: (lat: {original_lat}, lng: {original_lng})")
    print(f"平移距离: 向北 {offset_n} 米, 向东 {offset_e} 米")
    print(f"新坐标:   (lat: {new_latitude}, lng: {new_longitude})")
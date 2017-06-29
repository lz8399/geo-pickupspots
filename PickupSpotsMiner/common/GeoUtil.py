# -*- coding: utf-8 -*-

from math import radians, cos, sin, asin, sqrt
import math
import Geohash

earthR = 6378137.0


# cachedir = mkdtemp()
# memory = Memory(cachedir=cachedir, mmap_mode='r', verbose=0)


# @memory.cache
def haversine(lat1, lon1, lat2, lon2):
    '''
    球面距离

    :param lat1: 纬度1
    :param lon1: 经度1
    :param lat2: 纬度2
    :param lon2: 精度2
    :return: 球面距离，单位：米
    '''
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # km
    return c * r * 1000


def outOfChina(lat, lng):
    '''
    坐标是否超出中国边界

    :param lat: 纬度
    :param lng: 经度
    :return: boolean
    '''

    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def transform(x, y):
    xy = x * y
    absX = math.sqrt(abs(x))
    xPi = x * math.pi
    yPi = y * math.pi
    d = 20.0 * math.sin(6.0 * xPi) + 20.0 * math.sin(2.0 * xPi)

    lat = d
    lng = d

    lat += 20.0 * math.sin(yPi) + 40.0 * math.sin(yPi / 3.0)
    lng += 20.0 * math.sin(xPi) + 40.0 * math.sin(xPi / 3.0)

    lat += 160.0 * math.sin(yPi / 12.0) + 320 * math.sin(yPi / 30.0)
    lng += 150.0 * math.sin(xPi / 12.0) + 300.0 * math.sin(xPi / 30.0)

    lat *= 2.0 / 3.0
    lng *= 2.0 / 3.0

    lat += -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * xy + 0.2 * absX
    lng += 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * xy + 0.1 * absX

    return lat, lng


def delta(lat, lng):
    ee = 0.00669342162296594323
    dLat, dLng = transform(lng - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((earthR * (1 - ee)) / (magic * sqrtMagic) * math.pi)
    dLng = (dLng * 180.0) / (earthR / sqrtMagic * math.cos(radLat) * math.pi)
    return dLat, dLng


def gcj2wgs(gcjLat, gcjLng):
    '''
    火星坐标转世界坐标

    :param gcjLat: 火星纬度
    :param gcjLng: 火星经度
    :return: (世界纬度， 世界经度)
    '''

    if outOfChina(gcjLat, gcjLng):
        return gcjLat, gcjLng
    else:
        dlat, dlng = delta(gcjLat, gcjLng)
        return gcjLat - dlat, gcjLng - dlng


def wgs2gcj(wgsLat, wgsLng):
    '''
    世界坐标转火星坐标

    :param gcjLat: 世界纬度
    :param gcjLng: 世界经度
    :return: (火星纬度， 火星经度)
    '''

    if outOfChina(wgsLat, wgsLng):
        return wgsLat, wgsLng
    else:
        dlat, dlng = delta(wgsLat, wgsLng)
        return wgsLat + dlat, wgsLng + dlng


# @memory.cache
def geohash_encoding(gcjLat, gcjLng, precision=12):
    '''
    geohash编码，火星坐标转世界坐标后编码

    :param gcjLat: 火星纬度
    :param gcjLng: 火星经度
    :param precision: geohash编码精度
    :return: geohash code 字符串
    '''

    if not isinstance(gcjLat, float) or not isinstance(gcjLng, float):
        raise ValueError("input lat and lng is not float")
    if not isinstance(precision, int):
        raise ValueError("input precision is not int")
    if not 1 <= precision <= 12:
        raise ValueError("precision must between 1 and 12")
    wgsLat, wgsLng = gcj2wgs(gcjLat, gcjLng)
    return Geohash.encode(wgsLat, wgsLng, precision)


def geohash_decoding(geohash):
    '''
    geohash 逆转换为火星坐标对

    :param geohash: 待转换的geohash
    :return: (火星坐标纬度，火星坐标经度)
    '''

    wgsLat, wgsLng = Geohash.decode(geohash)
    return wgs2gcj(wgsLat, wgsLng)


if __name__ == "__main__":
    print geohash_encoding(39.9838536328, 116.3101251705)
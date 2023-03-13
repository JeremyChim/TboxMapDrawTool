# coding:GBK
import codecs
import math
import re
import datetime
import time

class DataFilter:

    def __init__(self,file_path):
        '''输入log的文件路径，进行参数初始化'''
        self.logfile = codecs.open(file_path, encoding="GBK", errors='ignore')
        self.keyword = "GNGGA"
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0  # 圆周率π
        self.pi = 3.1415926535897932384626  # 长半轴长度
        self.a = 6378245.0  # 地球的角离心率
        self.ee = 0.00669342162296594323  # 矫正参数
        self.interval = 0.000001
        self.locations = []
        self.dtime = []

    def return_locations_dtime(self):
        '''输出位置的坐标和时间'''
        for line in self.logfile.readlines():
            if self.keyword in line:
                line = line.strip()     # strip()去掉每列前后的空格
                sp = line.split(',')
                if sp[2] != '' and sp[4] != '':     # 判断字段（经纬度）不为空时，处理数据

                    # 获取时间
                    match_str = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                    res = datetime.datetime.strptime(match_str.group(), '%Y-%m-%d %H:%M:%S')

                    lat = float(sp[2])
                    lat = int(lat / 100) + ((lat / 100) - int(lat / 100)) * 100 / 60    # 纬度ddmm.mmmm，度分格式->度点度
                    lon = float(sp[4])
                    lon = int(lon / 100) + ((lon / 100) - int(lon / 100)) * 100 / 60

                    self.locations.append(self.wgs84_to_gcj02(lat, lon))    # 把经纬度添加进列表中
                    self.dtime.append(res)    # 把位置的时间添加进列表中

        self.logfile.close()
        return self.locations, self.dtime

    def return_locations_dtime_after_timefilter(self,start_time:str,end_time:str):
        '''输出筛选过后坐标和时间'''
        for line in self.logfile.readlines():
            if self.keyword in line:
                line = line.strip()     # strip()去掉每列前后的空格
                sp = line.split(',')
                if sp[2] != '' and sp[4] != '':     # 判断字段（经纬度）不为空时，处理数据

                    # 获取时间
                    match_str = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                    res = datetime.datetime.strptime(match_str.group(), '%Y-%m-%d %H:%M:%S')

                    lat = float(sp[2])
                    lat = int(lat / 100) + ((lat / 100) - int(lat / 100)) * 100 / 60    # 纬度ddmm.mmmm，度分格式->度点度
                    lon = float(sp[4])
                    lon = int(lon / 100) + ((lon / 100) - int(lon / 100)) * 100 / 60

                    start_time_stamp = self.return_int_time_stamp(start_time)
                    flag_time_stamp = self.return_int_time_stamp(res)
                    end_time_stamp = self.return_int_time_stamp(end_time)

                    if start_time_stamp < flag_time_stamp < end_time_stamp:
                        self.locations.append(self.wgs84_to_gcj02(lat, lon))    # 把经纬度添加进列表中
                        self.dtime.append(res)    # 把位置的时间添加进列表中

        self.logfile.close()
        return self.locations, self.dtime

    def return_locations(self):
        '''输出位置的坐标'''
        for line in self.logfile.readlines():
            if self.keyword in line:
                line = line.strip()     # strip()去掉每列前后的空格
                sp = line.split(',')
                if sp[2] != '' and sp[4] != '':     # 判断字段（经纬度）不为空时，处理数据
                    lat = float(sp[2])
                    lat = int(lat / 100) + ((lat / 100) - int(lat / 100)) * 100 / 60    # 纬度ddmm.mmmm，度分格式->度点度
                    lon = float(sp[4])
                    lon = int(lon / 100) + ((lon / 100) - int(lon / 100)) * 100 / 60
                    self.locations.append(self.wgs84_to_gcj02(lat, lon))    # 把经纬度添加进列表中
        self.logfile.close()
        return self.locations

    def return_dtime(self):
        '''输出位置的时间'''
        for line in self.logfile.readlines():
            if self.keyword in line:
                line = line.strip()  # strip()去掉每列前后的空格
                sp = line.split(',')
                if sp[2] != '' and sp[4] != '':     # 判断字段（经纬度）不为空时，处理数据
                    # 获取时间
                    match_str = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                    res = datetime.datetime.strptime(match_str.group(), '%Y-%m-%d %H:%M:%S')
                    self.dtime.append(res)    # 把位置的时间添加进列表中
        self.logfile.close()
        return self.dtime

    def return_int_time_stamp(self,valid_time:str):
        '''将str类型的时间转换成int类型时间戳，转换格式为%Y-%m-%d %H:%M:%S'''
        dd = time.strptime(str(valid_time), '%Y-%m-%d %H:%M:%S')
        ts = int(time.mktime(dd))
        return ts

    def _transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 *
                math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 *                math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 *
                math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 *
                math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def wgs84_to_gcj02(self, lat, lng):
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        gclng = lng + dlng
        gclat = lat + dlat
        return [gclat, gclng]

if __name__ == '__main__':
    from tkinter import filedialog

    st = '2023-2-15 11:30:00'
    print(type(st))
    et = '2023-2-15 12:0:0'

    _path = filedialog.askopenfilename()    # 载入日志文件
    log_df = DataFilter(_path)  # 输入log的文件路径，进行参数初始化
    _locations,_dtime = log_df.return_locations_dtime_after_timefilter(start_time=st, end_time=et)    # 输出筛选过后坐标和时间
    print(_locations,_dtime)


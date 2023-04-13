import pathlib
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import threading
import function.DataFilter.DataFilter as df
import function.MapDraw.MapDraw as md
import function.WriteExcel.WriteExcel as we

class MapDrawTool(ttk.Frame):
    '''该class是地图打点工具的内部框架布局'''

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.key_var = ttk.StringVar(value="GNGGA")
        self.key_list = ["GNGGA","GPGGA"]
        self.map_var = ttk.StringVar(value='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}')
        self.point_cheak_var = ttk.StringVar(value='on')
        self.link_cheak_var = ttk.StringVar(value='on')
        self.point_var = ttk.StringVar(value='blue')
        self.link_var = ttk.StringVar(value='red')
        self.time_cheak_var = ttk.StringVar(value='off')
        self.draw_accuracy_var = ttk.StringVar(value=1)
        self.draw_progress_var = ttk.StringVar(value=0)
        self.link_opacity_var = ttk.StringVar(value=0.8)

        self.menu_row = ttk.Frame(self)
        self.menu_row.pack(fill=X, expand=YES, pady=(0,15))

        file_text = '日志'
        self.file_lf = ttk.Labelframe(self, text=file_text, padding=15)
        self.file_lf.pack(fill=X, expand=YES, anchor=N)

        style_text = '风格'
        self.style_lf = ttk.Labelframe(self, text=style_text, padding=15)
        self.style_lf.pack(fill=X, expand=YES, anchor=N, pady=(15,0))

        timer_text = '时间筛选'
        self.timer_lf = ttk.Labelframe(self, text=timer_text, padding=15)
        self.timer_lf.pack(fill=X, expand=YES, anchor=N, pady=(15,0))

        draw_text = '打点'
        self.draw_lf = ttk.Labelframe(self, text=draw_text, padding=15)
        self.draw_lf.pack(fill=X, expand=YES, anchor=N, pady=(15,0))

        var = '轨迹透明度'
        self.create_menu_row()
        self.create_path_row()
        self.create_key_row()
        self.create_map_row()
        self.create_point_row()
        self.create_link_row()
        self.create_draw_accuracy_row()
        self.create_link_opacity_row(var)
        self.create_time_cheak_row()
        self.create_start_time_row()
        self.create_end_time_row()
        self.create_draw_row()

    def create_menu_row(self):
        '''创建一个菜单行'''
        _style = ttk.Style()
        _theme_name = _style.theme_names()

        about_btn = ttk.Button(
            master=self.menu_row,
            text='关于',
            command=self.about,
            width=8,
            bootstyle=OUTLINE
        )
        about_btn.pack(side=LEFT)

        theme_lbl = ttk.Label(master=self.menu_row,
                        text='主题：')

        self.theme_cb = ttk.Combobox(master=self.menu_row,
                               values=_theme_name,
                               width=10)

        theme_btn = ttk.Button(master=self.menu_row,
                         text='应用',
                         command=self.change_theme
                         )

        theme_btn.pack(side=RIGHT, padx=5)
        self.theme_cb.pack(side=RIGHT)
        theme_lbl.pack(side=RIGHT)

        self.theme_cb.current(_theme_name.index(_style.theme.name)) # 将初始主题名索引

    def create_path_row(self):
        '''该def是path路径行的框架布局'''
        path_row = ttk.Frame(self.file_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text='路径', width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row,
            text='浏览',
            command=self.on_browse,
            width=8,
            # bootstyle=OUTLINE
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_key_row(self):
        key_row = ttk.Frame(self.file_lf)
        key_row.pack(fill=X, expand=YES, pady=(15, 0))

        key_lbl = ttk.Label(key_row, text='关键字')
        key_lbl.pack(side=LEFT, padx=15)

        key_cb = ttk.Combobox(key_row,
                                   textvariable=self.key_var,
                                   values=self.key_list)

        key_cb.pack(side=LEFT, padx=15 ,fill=X, expand=YES)

    def create_draw_row(self):
        '''将draw行添加至标签框架'''
        draw_row = ttk.Frame(self.draw_lf)
        draw_row.pack(fill=X, expand=YES)
        draw_pgb_row = ttk.Frame(self.draw_lf)
        draw_pgb_row.pack(fill=X, expand=YES)

        export_excel_btn = ttk.Button(
            master=draw_row,
            text='生成Excel表',
            width=37,
            bootstyle=WARNING,
            command=self.pull_excel
            # bootstyle=(DANGER,OUTLINE),
        )

        draw_btn = ttk.Button(
            master=draw_row,
            text='开始地图打点和轨迹绘制',
            width=37,
            bootstyle=DANGER,
            command=self.map_draw
            # bootstyle=(DANGER,OUTLINE),
        )

        self.draw_pgb = ttk.Progressbar(
            master=draw_pgb_row,
            bootstyle='success-striped',
            orient='horizontal',
            mode='determinate',
            maximum = 1,
            value = self.draw_progress_var.get()
        )

        # draw_pgb.start()    #进度条动动看
        export_excel_btn.pack(side=LEFT, expand=YES, padx=0, fill=X)
        draw_btn.pack(side=LEFT, expand=YES, padx=0, fill=X)
        self.draw_pgb.pack(fill=X)

    def create_map_row(self):
        '''将map行添加至标签框架'''
        map_row = ttk.Frame(self.style_lf)
        map_row.pack(fill=X, expand=YES)
        map_lbl = ttk.Label(map_row, text='地图源', width=9)
        map_lbl.pack(side=LEFT, padx=15)

        amap_street_rb = ttk.Radiobutton(
            master=map_row,
            text='高德街道图',
            variable=self.map_var,
            value='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}'
        )
        amap_street_rb.pack(side=LEFT, padx=(15,0))
        amap_street_rb.invoke()

        amap_satellite_rb = ttk.Radiobutton(
            master=map_row,
            text='高德卫星图',
            variable=self.map_var,
            value='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
        )
        amap_satellite_rb.pack(side=LEFT, padx=(15,0))

        tencent_street_rb = ttk.Radiobutton(
            master=map_row,
            text='腾讯街道图',
            variable=self.map_var,
            value='http://rt1.map.gtimg.com/realtimerender?z={z}&x={x}&y={-y}&type=vector&style=6'
        )
        tencent_street_rb.pack(side=LEFT, padx=(15,0))

        google_street_rb = ttk.Radiobutton(
            master=map_row,
            text='谷歌街道图',
            variable=self.map_var,
            value='https://mt.google.com/vt/lyrs=h&x={x}&y={y}&z={z}'
        )
        google_street_rb.pack(side=LEFT, padx=(15,0))

        google_satellite_rb = ttk.Radiobutton(
            master=map_row,
            text='谷歌卫星图',
            variable=self.map_var,
            value='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
        )
        google_satellite_rb.pack(side=LEFT, padx=(15,0))

    def create_point_row(self):
        '''将point行添加至标签框架'''
        point_row = ttk.Frame(self.style_lf)
        point_row.pack(fill=X, expand=YES , pady=15)
        point_lbl = ttk.Label(point_row, text='途经点风格', width=9)
        point_lbl.pack(side=LEFT, padx=15)

        point_cb = ttk.Checkbutton(
            master=point_row,
            text='',
            bootstyle=(SUCCESS, ROUND, TOGGLE),
            variable=self.point_cheak_var,
            onvalue='on',
            offvalue='off'
        )
        point_cb.pack(side=LEFT, padx=15)

        blue_point_rb = ttk.Radiobutton(
            master=point_row,
            text='蓝点',
            variable=self.point_var,
            value='blue'
        )
        blue_point_rb.pack(side=LEFT, padx=15)
        blue_point_rb.invoke()

        red_point_rb = ttk.Radiobutton(
            master=point_row,
            text='红点',
            variable=self.point_var,
            value='red'
        )
        red_point_rb.pack(side=LEFT, padx=15)

        pink_point_rb = ttk.Radiobutton(
            master=point_row,
            text='粉点',
            variable=self.point_var,
            value='pink'
        )
        pink_point_rb.pack(side=LEFT, padx=15)

        orange_point_rb = ttk.Radiobutton(
            master=point_row,
            text='橙点',
            variable=self.point_var,
            value='orange'
        )
        orange_point_rb.pack(side=LEFT, padx=15)

        gps_point_rb = ttk.Radiobutton(
            master=point_row,
            text='紫点',
            variable=self.point_var,
            value='purple'
        )
        gps_point_rb.pack(side=LEFT, padx=15)

    def create_link_row(self):
        link_row = ttk.Frame(self.style_lf)
        link_row.pack(fill=X, expand=YES)
        link_lbl = ttk.Label(link_row, text='轨迹风格', width=9)
        link_lbl.pack(side=LEFT, padx=15)

        link_cb = ttk.Checkbutton(
            master=link_row,
            text='',
            bootstyle=(SUCCESS, ROUND, TOGGLE),
            variable=self.link_cheak_var,
            onvalue='on',
            offvalue='off'
        )
        link_cb.pack(side=LEFT, padx=15)

        red_link_rb = ttk.Radiobutton(
            master=link_row,
            text='红线',
            variable=self.link_var,
            value='red'
        )
        red_link_rb.pack(side=LEFT, padx=15)
        red_link_rb.invoke()

        blue_link_rb = ttk.Radiobutton(
            master=link_row,
            text='蓝线',
            variable=self.link_var,
            value='blue'
        )
        blue_link_rb.pack(side=LEFT, padx=15)

        green_link_rb = ttk.Radiobutton(
            master=link_row,
            text='绿线',
            variable=self.link_var,
            value='green'
        )
        green_link_rb.pack(side=LEFT, padx=15)

        orange_link_rb = ttk.Radiobutton(
            master=link_row,
            text='橙线',
            variable=self.link_var,
            value='orange'
        )
        orange_link_rb.pack(side=LEFT, padx=15)

        pink_link_rb = ttk.Radiobutton(
            master=link_row,
            text='粉线',
            variable=self.link_var,
            value='pink'
        )
        pink_link_rb.pack(side=LEFT, padx=15)

    def create_link_opacity_row(self,text):
        link_opacity_row = ttk.Frame(self.style_lf)
        link_opacity_row.pack(fill=X, expand=YES, pady=(15,0))
        link_opacity_lbl = ttk.Label(link_opacity_row, text='轨迹透明度', width=9)
        link_opacity_lbl.pack(side=LEFT, padx=15)

        # self.link_opacity_var(text,value)
        value = 0.8
        self.setvar(text, value)

        link_opacity_scl = ttk.Scale(
            master=link_opacity_row,
            orient=HORIZONTAL,
            style=DANGER,
            value=value,
            from_=0,
            to=1,
            command=lambda x=value, y=text: self.update_value(x, y))
        link_opacity_scl.pack(side=LEFT,padx=(15,0),fill=X, pady=5, expand=YES)

        link_opacity_lbl2 = ttk.Label(link_opacity_row, textvariable=text, width=9)
        link_opacity_lbl2.pack(side=RIGHT, padx=(10,300))

    def update_value(self, value, name):
        self.setvar(name, f'{float(value):.1f}')
        self.link_opacity_var.set(value=value)

    def create_draw_accuracy_row(self):
        draw_accuracy_row = ttk.Frame(self.style_lf)
        draw_accuracy_row.pack(fill=X, expand=YES, pady=(15,0))
        draw_accuracy_lbl = ttk.Label(draw_accuracy_row, text='坐标点数量', width=9)
        draw_accuracy_lbl.pack(side=LEFT, padx=15)

        draw_all_rb = ttk.Radiobutton(
            master=draw_accuracy_row,
            text='全部',
            variable=self.draw_accuracy_var,
            value=1
        )
        draw_all_rb.pack(side=LEFT, padx=15)
        draw_all_rb.invoke()

        draw_2_1_rb = ttk.Radiobutton(
            master=draw_accuracy_row,
            text='一半',
            variable=self.draw_accuracy_var,
            value=2
        )
        draw_2_1_rb.pack(side=LEFT, padx=15)

        draw_3_1_rb = ttk.Radiobutton(
            master=draw_accuracy_row,
            text='三分之一',
            variable=self.draw_accuracy_var,
            value=3
        )
        draw_3_1_rb.pack(side=LEFT, padx=15)

        draw_4_1_rb = ttk.Radiobutton(
            master=draw_accuracy_row,
            text='四分之一',
            variable=self.draw_accuracy_var,
            value=4
        )
        draw_4_1_rb.pack(side=LEFT, padx=15)

        draw_5_1_rb = ttk.Radiobutton(
            master=draw_accuracy_row,
            text='五分之一',
            variable=self.draw_accuracy_var,
            value=5
        )
        draw_5_1_rb.pack(side=LEFT, padx=15)

    def create_time_cheak_row(self):
        time_cheak_row = ttk.Frame(self.timer_lf)
        time_cheak_row.pack(fill=X, expand=YES)
        time_cb = ttk.Checkbutton(
            master=time_cheak_row,
            text='',
            bootstyle=(SUCCESS, ROUND, TOGGLE),
            variable=self.time_cheak_var,
            onvalue='on',
            offvalue='off'
        )
        time_cb.pack(side=LEFT, padx=15)
        # time_cb.invoke()

    def create_start_time_row(self):
        start_time_row = ttk.Frame(self.timer_lf)
        start_time_row.pack(fill=X, expand=YES, pady=15)
        start_time_lbl = ttk.Label(start_time_row, text='开始时间', width=8)
        start_time_lbl.pack(side=LEFT, padx=15)

        self.start_date_de = ttk.DateEntry(start_time_row)
        self.start_date_de.pack(side=LEFT)

        self.start_hour_sb = ttk.Spinbox(
            master=start_time_row,
            width=2,
            from_=0,
            to=23)
        self.start_hour_sb.pack(side=LEFT, padx=(30,5))
        self.start_hour_sb.set(0)

        start_hour_lbl = ttk.Label(start_time_row, text='时')
        start_hour_lbl.pack(side=LEFT)

        self.start_minute_sb = ttk.Spinbox(
            master=start_time_row,
            width=2,
            from_=0,
            to=59)
        self.start_minute_sb.pack(side=LEFT, padx=(15,5))
        self.start_minute_sb.set(0)

        start_minute_lbl = ttk.Label(start_time_row, text='分')
        start_minute_lbl.pack(side=LEFT)

        self.start_second_sb = ttk.Spinbox(
            master=start_time_row,
            width=2,
            from_=0,
            to=59)
        self.start_second_sb.pack(side=LEFT, padx=(15,5))
        self.start_second_sb.set(0)

        start_second_lbl = ttk.Label(start_time_row, text='秒')
        start_second_lbl.pack(side=LEFT)

    def create_end_time_row(self):
        end_time_row = ttk.Frame(self.timer_lf)
        end_time_row.pack(fill=X, expand=YES)
        end_time_lbl = ttk.Label(end_time_row, text='结束时间', width=8)
        end_time_lbl.pack(side=LEFT, padx=15)

        self.end_date_de = ttk.DateEntry(end_time_row)
        self.end_date_de.pack(side=LEFT)

        self.end_hour_sb = ttk.Spinbox(
            master=end_time_row,
            width=2,
            from_=0,
            to=23)
        self.end_hour_sb.pack(side=LEFT, padx=(30,5))
        self.end_hour_sb.set(0)

        end_hour_lbl = ttk.Label(end_time_row, text='时')
        end_hour_lbl.pack(side=LEFT)

        self.end_minute_sb = ttk.Spinbox(
            master=end_time_row,
            width=2,
            from_=0,
            to=59)
        self.end_minute_sb.pack(side=LEFT, padx=(15,5))
        self.end_minute_sb.set(0)

        end_minute_lbl = ttk.Label(end_time_row, text='分')
        end_minute_lbl.pack(side=LEFT)

        self.end_second_sb = ttk.Spinbox(
            master=end_time_row,
            width=2,
            from_=0,
            to=59)
        self.end_second_sb.pack(side=LEFT, padx=(15,5))
        self.end_second_sb.set(0)

        end_second_lbl = ttk.Label(end_time_row, text='秒')
        end_second_lbl.pack(side=LEFT)

    def on_browse(self):
        '''打开文件浏览器，并输出选中的文件路径'''
        path = filedialog.askopenfilename(title='选择日志文件')
        if path:
            self.path_var.set(path)

    def about(self):
        tk.messagebox.showinfo('关于 TBOX地图打点工具',
                               '作者：Mavis\n'
                               '版本：v2.3\n'
                               '时间：2023-04-13\n'
                               '思路提供：家文同学\n'
                               '测试：戴少\n'
                               '设计：Jer小铭'
                               '\n\n特别鸣谢各位大神对本程序的大力支持')

    def link_opacity_var_float(self):
        '''将轨迹的透明度转换成小数点后一位的float参数并输出'''
        float_var = float('%.1f' % float(self.link_opacity_var.get()))
        # print(type(float_var))
        # print(float_var)
        return float_var

    def return_start_datetime(self):
        '''返回str类的开始时间数据'''
        date = self.start_date_de.entry.get()
        date = date.replace('/' , '-')  #把 / 替换成 -
        hour = self.start_hour_sb.get()
        minute = self.start_minute_sb.get()
        second = self.start_second_sb.get()
        _datetime = f'{date} {hour}:{minute}:{second}'
        return _datetime

    def return_end_datetime(self):
        '''返回str类的结束时间数据'''
        date = self.end_date_de.entry.get()
        date = date.replace('/' , '-')  #把 / 替换成 -
        hour = self.end_hour_sb.get()
        minute = self.end_minute_sb.get()
        second = self.end_second_sb.get()
        _datetime = f'{date} {hour}:{minute}:{second}'
        return _datetime

    def map_draw(self):
        '''执行地图打点的动作'''
        print('开始启动打点程序...')
        print(f'log路径: {self.path_var.get()}')
        print(f'关键字: {self.key_var.get()}')
        print(f'轨迹风格: {self.link_var.get()}')
        print(f'途经点风格: {self.point_var.get()}')
        print(f'地图源：{self.map_var.get()}')
        print(f'轨迹开关: {self.link_cheak_var.get()}')
        print(f'打点精度: {self.draw_accuracy_var.get()}')
        print(f'轨迹透明度: {self.link_opacity_var_float()}')
        print(f'时间筛选开关：{self.time_cheak_var.get()}')
        print(f'开始时间：{self.return_start_datetime()}')
        print(f'结束时间：{self.return_end_datetime()}')
        print('-' * 50)

        _path = self.path_var.get()   # 载入log的文件路径
        _key = self.key_var.get()    # 载入关键字
        log_df = df.DataFilter(file_path=_path, keyword=_key)    # 输入log的文件路径，进行参数初始化

        if self.time_cheak_var.get() == 'on':
            locations_list, dtime_list = log_df.return_locations_dtime_after_timefilter(
                start_time = self.return_start_datetime() ,
                end_time = self.return_end_datetime()
            )   # 输出筛选过后坐标和时间
        else:
            locations_list = log_df.return_locations() # 输出位置的坐标

        if len(locations_list) == 0:
            tk.messagebox.showinfo('无坐标数据',
                                   '未找到定位坐标数据，请检查筛选的时间或者导入的GPS日志')

        else:
            log_to_map = md.MapDraw(locations=locations_list,
                                    link_color=self.link_var.get(),
                                    link_opacity=self.link_opacity_var_float(),
                                    point_color=self.point_var.get(),
                                    point_coefficient=int(self.draw_accuracy_var.get()),
                                    map_source=self.map_var.get(),
                                    )

            if self.link_cheak_var.get() == 'on':
                log_to_map.create_link()
            if self.point_cheak_var.get() == 'on':
                log_to_map.create_point()

            t1 = threading.Thread(target=self.update_progress(locations_list))
            t1.start()
            log_to_map.open_map()
            self.draw_pgb['value'] = 1
            self.draw_pgb.update()

    def pull_excel(self):
        '''执行导出Excel表的动作'''

        _path = self.path_var.get()   # 载入log的文件路径
        _key = self.key_var.get()  # 载入关键字
        log_df = df.DataFilter(file_path=_path, keyword=_key)    # 输入log的文件路径，进行参数初始化

        if self.time_cheak_var.get() == 'on':
            locations_list, dtime_list = log_df.return_locations_dtime_after_timefilter(
                start_time = self.return_start_datetime() ,
                end_time = self.return_end_datetime()
            )   # 输出筛选过后坐标和时间
        else:
            locations_list, dtime_list = log_df.return_locations_dtime() # 输出位置的坐标和时间

        if len(locations_list) == 0:
            tk.messagebox.showinfo('无坐标数据',
                                   '未找到定位坐标数据，请检查筛选的时间或者导入的GPS日志')

        else:
            t2 = threading.Thread(target=self.update_progress(locations_list))
            t2.start()
            we.write_to_excel(locations = locations_list,
                              dtime = dtime_list
                              )
            tk.messagebox.showinfo('生成Excel表完成',
                                   '已将定位坐标值和时间导入到Excel表，并生成在根目录')
            self.draw_pgb['value'] = 1
            self.draw_pgb.update()

    def update_progress(self, locations):
        for i in range(1, len(locations) + 1, 10):
            self.draw_pgb['value'] = i / len(locations)
            self.draw_pgb.update()

    def change_theme(self):
        '''获取theme_cb的值（主题名），并应用主题'''
        print(f'正在应用主题：{self.theme_cb.get()}')
        t = self.theme_cb.get()
        ttk.Style().theme_use(t)

if __name__ == '__main__':

    app = ttk.Window('TBOX地图打点工具', 'litera')
    MapDrawTool(app)
    version = ttk.Label(app, text='版本：v2.3')
    version.pack(side=RIGHT, padx=15)
    app.place_window_center()    #让显现出的窗口居中
    # app.resizable(False,False)   #让窗口不可更改大小
    app.mainloop()
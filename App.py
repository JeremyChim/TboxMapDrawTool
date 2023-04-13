import ttkbootstrap as ttk
from ttkbootstrap.constants import *
#导入第三方库

import ui.Window as ui
#
#导入自定义函数

app = ttk.Window("TBOX地图打点工具", "litera")
ui.MapDrawTool(app)

version = ttk.Label(app, text="版本：v2.1")
version.pack(side=RIGHT, padx=15, pady=1)

app.place_window_center()    #让显现出的窗口居中
app.resizable(False,False)   #让窗口不可更改大小

app.mainloop()
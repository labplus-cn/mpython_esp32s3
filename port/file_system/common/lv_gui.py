
import time, math, struct
import utime
import lvgl as lv
import adafruit_miniqr
import lcd
import lv_displayer
from mpython import button_a, button_b
from font.digital_dot_matrix import DOT_MATRIX

from lv_utils import event_loop


GUI_ATTR = {
    "font_size": {
        # "16": lv.font_siyuan_heiti_medium_16,
        "24": lv.font_siyuan_heiti_medium_24
    },
    "label_long_mode": {
        'clip': lv.label.LONG_MODE.CLIP, # 超出隐藏
        'wrap': lv.label.LONG_MODE.WRAP, # 自动换行
        'dots': lv.label.LONG_MODE.DOTS, # 溢出省略号代替
        'scroll': lv.label.LONG_MODE.SCROLL, # 水平来回滚动
        'scroll_circular': lv.label.LONG_MODE.SCROLL_CIRCULAR, # 水平循环滚动
    },
    "text_flag": {
        "none": lv.TEXT_FLAG.NONE,
        "break_all": lv.TEXT_FLAG.BREAK_ALL,
        "expand": lv.TEXT_FLAG.EXPAND,
        "fit": lv.TEXT_FLAG.FIT
    },
    "chart_type": {
        "none": lv.chart.TYPE.NONE,
        "line": lv.chart.TYPE.LINE,
        "bar": lv.chart.TYPE.BAR,
        "scatter": lv.chart.TYPE.SCATTER
    },
    "anim": {
        "off": 0, # lv.ANIM.OFF,
        "on": 1 # lv.ANIM.ON
    },
    'scale_mode': {
        'hor_bottom': lv.scale.MODE.HORIZONTAL_BOTTOM,
        'ver_right': lv.scale.MODE.VERTICAL_RIGHT,
        'round_inner': lv.scale.MODE.ROUND_INNER
    }
}

class LV_GUI:
    def __init__(self, scr = None, group = False):
        self.loop_cb = None
        self.loop_event = None
        self.bg_color = 0x000000
        self.scr = scr if scr else lv.screen_active()
        self.width = 320
        self.height = 172
        self.init_obj_style()

        if group:
            self.key_is_end = None
            self.key_pressed = None
            self.create_group()
    
    def init_obj_style(self):
        self.obj_sty = lv.style_t()
        self.obj_sty.init()
        self.obj_sty.set_pad_all(0)
        self.obj_sty.set_radius(0)
        self.obj_sty.set_border_width(0)

    # A、B按键监听
    def gui_detect_key(self):
        if self.key_is_end is None:
            if button_a.is_pressed():   #按键被按下
                time.sleep_ms(50) #消除抖动
                if button_a.is_pressed(): #确认按键被按下
                    self.key_is_end = 'btn_a'
                    self.key_pressed = lv.KEY.ENTER

            elif button_b.is_pressed():   #按键被按下
                time.sleep_ms(50) #消除抖动
                if button_b.is_pressed(): #确认按键被按下
                    self.key_is_end = 'btn_b'
                    self.key_pressed = lv.KEY.NEXT
                    
        elif self.key_is_end and (not button_a.is_pressed()) and (not button_b.is_pressed()):
            self.key_is_end = None

    # 输入设备按下响应回调
    def my_input_read(self, indev_drv, data):
        self.gui_detect_key()
        if self.key_pressed is not None:
            data.key = self.key_pressed
            data.state = lv.INDEV_STATE.PRESSED
            self.key_pressed = None  # 清除按键状态
        else:
            data.state = lv.INDEV_STATE.RELEASED
        return False  # 表示没有更多数据

    # 创建输入设备组并绑定
    def create_group(self):
        self.group = lv.group_create()
        # 创建输入设备
        indev = lv.indev_create()
        indev.set_type(lv.INDEV_TYPE.KEYPAD)  # 设为键盘输入
        indev.set_read_cb(self.my_input_read)      # 绑定回调
        # 绑定到 group
        indev.set_group(self.group)

    def deinit(self):
        pass


class CANVAS(LV_GUI):
    def __init__(self, scr = None):
        super().__init__(scr)
        self.c_label_lh = 32
        self.clocks = {}
        self.init_canvas()
        self.scr.set_scroll_dir(lv.DIR.NONE)
    
    def init_canvas(self):
        self.draw_buf = bytearray(self.width * self.height * 4)
        self.canvas = lv.canvas(self.scr)
        self.canvas.set_buffer(self.draw_buf, self.width, self.height, lv.COLOR_FORMAT.ARGB8888)
        self.canvas.center()
        self.canvas.fill_bg(lv.color_hex(self.bg_color), lv.OPA.COVER)
        self.layer = lv.layer_t()
        self.canvas.init_layer(self.layer)
    
    def update(self):
        self.canvas.finish_layer(self.layer)
        time.sleep(0.02)
        lv.task_handler()

    def set_bg_color(self, color=0x000000):
        self.bg_color = color
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(self.bg_color)
        dsc.bg_opa = lv.OPA.COVER
        coords = lv.area_t()
        coords.x1 = 0
        coords.y1 = 0
        coords.x2 = 320
        coords.y2 = 172
        lv.draw_rect(self.layer, dsc, coords)
    
    def clear(self, x=0, y=0, width=320, heght=172, row=None):
        if row:
            y = (row - 1) * self.c_label_lh + 4
            heght = y + self.c_label_lh
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(self.bg_color)
        dsc.bg_opa = lv.OPA.COVER
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = width
        coords.y2 = heght
        lv.draw_rect(self.layer, dsc, coords)
    
    def fill(self, x=0, y=0, width=320, heght=172, type=0):
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        color = self.bg_color
        if type == 2: color = 0x000000
        elif type == 3: color = 0xffffff
        dsc.bg_color = lv.color_hex(color)
        dsc.bg_opa = lv.OPA.COVER
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = width
        coords.y2 = heght
        lv.draw_rect(self.layer, dsc, coords)
    
    def draw_label(self, text, x=10, y=10, row=None, width=200, font_size=24, color=0xffffff, wrap=False):
        if row:
            x = 10
            y = (row - 1) * self.c_label_lh
            width = self.width - x
        dsc = lv.draw_label_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color)
        dsc.font = GUI_ATTR['font_size'].get(str(font_size))
        dsc.opa = lv.OPA.COVER
        dsc.flag = GUI_ATTR['text_flag'].get('break_all' if wrap else 'fit')
        dsc.line_space = -13
        dsc.text = text
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = x + width
        coords.y2 = y + self.c_label_lh
        lv.draw_label(self.layer, dsc, coords)

    def draw_point(self, x=10, y=10, color=0xffffff, state=1):
        dsc = lv.draw_arc_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color) if state else lv.color_hex(self.bg_color)
        dsc.center.x = x
        dsc.center.y = y
        dsc.width = 2
        dsc.radius = 2
        dsc.start_angle = 0
        dsc.end_angle = 360
        lv.draw_arc(self.layer, dsc)
    
    def draw_progress_bar(self, x=10, y=10, width=200, height=20, progress=20, border_color=0xffffff, bg_color=0xffff00):
        progress = progress if progress <= 100 else 100
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_opa = lv.OPA._0
        dsc.border_color = lv.color_hex(border_color)
        dsc.border_width = 2
        dsc.radius = math.floor(height / 2)
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = width + x
        coords.y2 = height + y
        lv.draw_rect(self.layer, dsc, coords)
        dsc1 = lv.draw_rect_dsc_t()
        dsc1.init()
        dsc1.bg_color = lv.color_hex(bg_color)
        dsc1.border_width = 0
        dsc1.radius = math.floor(height / 2)
        coords1 = lv.area_t()
        coords1.x1 = x + 2
        coords1.y1 = y + 2
        coords1.x2 = round((width - 2) * (progress / 100)) + x
        coords1.y2 = height + y - 2
        lv.draw_rect(self.layer, dsc1, coords1)
    
    def draw_columnar_bar(self, x=10, y=10, width=200, height=20, progress=20, border_color=0xffffff, bg_color=0xffff00, type=0):
        if type:
            w = width
            width = height
            height = w
        progress = progress if progress <= 100 else 100
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_opa = lv.OPA._0
        dsc.border_color = lv.color_hex(border_color)
        dsc.border_width = 2
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = width + x
        coords.y2 = height + y
        lv.draw_rect(self.layer, dsc, coords)
        dsc1 = lv.draw_rect_dsc_t()
        dsc1.init()
        dsc1.bg_color = lv.color_hex(bg_color)
        dsc1.border_width = 0
        coords1 = lv.area_t()
        if type:
            h = round((height - 4) * (progress / 100))
            coords1.x1 = x + 2
            coords1.y1 = height - h - 2 + y
            coords1.x2 = width + x - 2
            coords1.y2 = height -2 + y
        else:
            coords1.x1 = x + 2
            coords1.y1 = y + 2
            coords1.x2 = round((width - 2) * (progress / 100)) + x
            coords1.y2 = height + y - 2
        lv.draw_rect(self.layer, dsc1, coords1)

    def draw_line(self, x1=10, y1=10, x2=200, y2=200, width=100, size=2, color=0xffffff, type=0, draw=0):
        if type == 1:
            x2 = width + x1
            y2 = y1
        elif type == 2:
            x2 = x1
            y2 = width + y1
        dsc = lv.draw_line_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color if draw else self.bg_color)
        dsc.width = size
        dsc.opa = lv.OPA.COVER
        dsc.p1.x = x1
        dsc.p1.y = y1
        dsc.p2.x = x2
        dsc.p2.y = y2
        lv.draw_line(self.layer, dsc)
        
    def draw_rect(self, x=10, y=10, width=200, height=100, border_width=2, border_color=0xff0000, bg_color=0xffff00, radius=6, fill=0, draw=0):
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(bg_color if draw else self.bg_color)
        dsc.bg_opa = lv.OPA.COVER if fill else lv.OPA._0
        dsc.border_color = lv.color_hex(border_color if draw else self.bg_color)
        dsc.border_width = border_width
        dsc.radius = radius
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = width + x
        coords.y2 = height + y
        lv.draw_rect(self.layer, dsc, coords)

    def draw_round(self, x=100, y=100, radius=50, border_width=2, border_color=0xff0000, bg_color=0xffff00, fill=1, draw=0):
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(bg_color if draw else self.bg_color)
        dsc.bg_opa = lv.OPA.COVER if fill else lv.OPA._0
        dsc.border_color = lv.color_hex(border_color if draw else self.bg_color)
        dsc.border_width = border_width
        dsc.radius = radius
        coords = lv.area_t()
        coords.x1 = x - radius
        coords.y1 = y - radius
        coords.x2 = x + radius
        coords.y2 = y + radius
        lv.draw_rect(self.layer, dsc, coords)
    
    def draw_triangle(self, x1=10, y1=100, x2=50, y2=10, x3=100, y3=100, border_width=2, color=0xffff00, fill=1, draw=0):
        if not draw:
            color = self.bg_color  # 使用背景色擦除
        vertices = [(x1, y1), (x2, y2), (x3, y3)]
        if not fill:
            # 空心：画三条边
            for i in range(3):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % 3]
                self.draw_line(x1=x1, y1=y1, x2=x2, y2=y2, size=border_width, color=color, draw=1)
        else:
            # 实心：先填充，再描边
            self._fill_polygon(vertices, color)
            for i in range(3):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % 3]
                self.draw_line(x1=x1, y1=y1, x2=x2, y2=y2, size=border_width, color=color, draw=1)

    def draw_star(self, x, y, radius, line_width=2, color=0xffff00, fill=1, draw=0):
        if not draw: color = self.bg_color
        # 计算内顶点半径，约为 radius * sin(18°)/sin(54°) ≈ radius * 0.382
        inner_radius = int(radius * 0.382)
        outer_points = []
        inner_points = []
        for i in range(5):
            # 外顶点，起始角度 90°，顺时针每隔 72°
            angle_outer = math.radians(90 + i * 72)
            ox = x + int(radius * math.cos(angle_outer))
            oy = y - int(radius * math.sin(angle_outer))  # 注意：y轴向下增长
            outer_points.append((ox, oy))
            # 内顶点，起始角度 90+36=126°，顺时针每隔 72°
            angle_inner = math.radians(90 + 36 + i * 72)
            ix = x + int(inner_radius * math.cos(angle_inner))
            iy = y - int(inner_radius * math.sin(angle_inner))
            inner_points.append((ix, iy))
        
        if not fill:
            # 空心：按照外、内顶点交替连接构成轮廓
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])
            star_points.append(outer_points[0])  # 封闭路径
            for i in range(len(star_points) - 1):
                p1 = star_points[i]
                p2 = star_points[i+1]
                self.draw_line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], size=line_width, color=color, draw=1)
        else:
            # 填充：先填充中心五边形，再填充每个尖角的三角形
            # 填充中心五边形（由所有内顶点构成，顺序为 0→1→2→3→4）
            self._fill_polygon(inner_points, color)
            
            # 填充每个尖角三角形：
            # 三角形顶点为：外顶点 i、内顶点 i、内顶点 (i-1)%5
            for i in range(5):
                triangle = [
                    outer_points[i],
                    inner_points[i],
                    inner_points[(i - 1) % 5]
                ]
                self._fill_polygon(triangle, color)
            
            # 最后绘制星形边框
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])
            star_points.append(outer_points[0])
            for i in range(len(star_points) - 1):
                p1 = star_points[i]
                p2 = star_points[i+1]
                self.draw_line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], size=line_width, color=color, draw=1)

    def _fill_polygon(self, vertices, color):
        # 计算多边形外包矩形的 y 范围
        min_y = min(y for (_, y) in vertices)
        max_y = max(y for (_, y) in vertices)
        # 对每个扫描行 y
        for y in range(min_y, max_y + 1):
            intersections = []
            n = len(vertices)
            # 遍历每条边
            for i in range(n):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % n]
                # 判断扫描线 y 是否与边相交
                if (y1 <= y < y2) or (y2 <= y < y1):
                    # 计算交点 x 坐标
                    x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(int(x_int))
            intersections.sort()
            # 每对交点之间绘制水平线
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = intersections[i]
                    x_end = intersections[i + 1]
                    self.draw_line(x1=x_start, y1=y, x2=x_end, y2=y, size=1, color=color, draw=1)
    
    def draw_img(self, x=10, y=10, path='', width=None, height=None, img_src=None):
        if not path and not img_src: return
        if img_src is None:
            data = None
            with open(path,'rb') as f:
                data = f.read()
            img_src = lv.image_dsc_t({
                'data_size': len(data),
                'data': data
            })
        if (width is None) or (height is None):
            img = lv.image(lv.screen_active())
            img.set_src(img_src)
            img.update_layout()
            width = img.get_width()
            height = img.get_height()
            img.delete()
        dsc = lv.draw_image_dsc_t()
        dsc.init()
        dsc.src = img_src
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = x + width - 1  # 假设图片宽度 50
        coords.y2 = y + height - 1  # 假设图片高度 50
        lv.draw_image(self.layer, dsc, coords)
    
    def draw_bitmap(self, x=0, y=0, width=0, height=0, bitmap_data=[], fg_color=0xFFFFFFFF, bg_color=0x00000000):
        """高速绘制 1-bit 位图数据到 ARGB8888 canvas，在 (x, y) 位置绘制"""
        if str(type(bitmap_data)) == "<class 'list'>":
            bitmap_data = bytearray(bitmap_data)
        else:
            self.draw_img(x=x, y=y, path=bitmap_data, width=width, height=height)
            return
        byte_index = 0
        for d_y in range(height):
            for d_x in range(width):
                if d_x % 8 == 0:
                    if byte_index >= len(bitmap_data): break
                    byte = bitmap_data[byte_index]
                    byte_index += 1
                bit = 7 - (d_x % 8)
                pixel_on = (byte >> bit) & 0x01
                color = fg_color if pixel_on else bg_color
                canvas_x = x + d_x
                canvas_y = y + d_y
                # 边界检查，避免越界写入
                if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                    offset = (canvas_y * self.width + canvas_x) * 4
                    struct.pack_into("<I", self.draw_buf, offset, color)
        self.canvas.invalidate()

    # 显示点阵时间（仿数码管）
    def draw_dot_digit(self, x=10, y=10, time_str="12:34", color=0xff0000, bg_color=None, pixel_size=1, pixel_spacing=1):
        # pixel_size 每个像素点大小（正方形）
        # pixel_spacing 点之间间距
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        fg = lv.color_hex(color)
        dsc.bg_color = fg
        dsc.bg_opa = lv.OPA.COVER
        for ch in time_str:
            row_data = DOT_MATRIX.get(ch, DOT_MATRIX.get('?'))
            for row_idx, row in enumerate(row_data):
                col_idx = 0
                while col_idx < len(row):
                    if row[col_idx] == 1:  # 只画前景
                        run_start = col_idx
                        while col_idx + 1 < len(row) and row[col_idx + 1] == 1:
                            col_idx += 1
                        run_end = col_idx
    
                        # 坐标计算
                        px1 = x + run_start * (pixel_size + pixel_spacing)
                        px2 = x + run_end * (pixel_size + pixel_spacing) + pixel_size - 1
                        py1 = y + row_idx * (pixel_size + pixel_spacing)
                        py2 = py1 + pixel_size - 1
    
                        coords = lv.area_t()
                        coords.x1, coords.y1, coords.x2, coords.y2 = px1, py1, px2, py2
                        lv.draw_rect(self.layer, dsc, coords)
    
                    col_idx += 1
            # 字符间隔
            x += len(row_data[0]) * (pixel_size + pixel_spacing) + 2
    
    def draw_qrcode(self, x=10, y=10, scale=4, color=0xffffff, _str=''):
        fg = 0xFF000000 + color      # ARGB8888 格式
        bg = 0xFF000000 + self.bg_color  # ARGB8888 背景色
        qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.L)
        qr.add_data(_str.encode())
        qr.make()
        for _y in range(qr.matrix.height):
            for _x in range(qr.matrix.width):
                pixel_color = fg if qr.matrix[_x, _y] else bg
                # 画一个 scale x scale 的小方块
                for dy in range(scale):
                    for dx in range(scale):
                        cx = x + _x * scale + dx
                        cy = y + _y * scale + dy
                        if 0 <= cx < self.width and 0 <= cy < self.height:
                            offset = (cy * self.width + cx) * 4
                            struct.pack_into("<I", self.draw_buf, offset, pixel_color)
        self.canvas.invalidate()
    
    def draw_clock(self, x=160, y=86, radius=80, bg_color=0x242f37, border_color=0x48585c, key='clock'):
        if (key not in self.clocks):
            self.clocks[key] = {
                "x": x,
                "y": y,
                "r": radius,
                "bg_c": bg_color,
                "bd_c": border_color,
            }
        x = self.clocks[key]['x']
        y = self.clocks[key]['y']
        r = self.clocks[key]['r']
        bg_c = self.clocks[key]['bg_c']
        bd_c = self.clocks[key]['bd_c']

        # 绘制表盘
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(bg_c)
        dsc.bg_opa = lv.OPA.COVER
        dsc.border_color = lv.color_hex(bd_c)
        dsc.border_width = 2
        dsc.radius = r
        coords = lv.area_t()
        coords.x1 = x - r
        coords.y1 = y - r
        coords.x2 = x + r
        coords.y2 = y + r
        lv.draw_rect(self.layer, dsc, coords)

        # 绘制表盘刻度
        for i in range(60):
            angle = i * 6  # 每刻度 6°
            rad = math.radians(angle - 90)
            color=0x536b7a
            # 刻度起点 & 终点
            x1 = int(x + (r - 6) * math.cos(rad))  # 靠近边缘
            y1 = int(y + (r - 6) * math.sin(rad))
            if i % 5 == 0:  # **整点（小时刻度）**
                color=0x999999
                x2 = int(x + (r - 16) * math.cos(rad))
                y2 = int(y + (r - 16) * math.sin(rad))
                width = 3  # 加粗
            else:  # **分钟刻度**
                x2 = int(x + (r - 12) * math.cos(rad))
                y2 = int(y + (r - 12) * math.sin(rad))
                width = 1  # 细线
            dsc = lv.draw_line_dsc_t()
            dsc.init()
            dsc.color = lv.color_hex(color)
            dsc.width = width
            dsc.opa = lv.OPA.COVER
            dsc.p1.x = x1
            dsc.p1.y = y1
            dsc.p2.x = x2
            dsc.p2.y = y2
            lv.draw_line(self.layer, dsc)
        
        # 绘制表盘数字
        for i in range(1, 13):
            angle = (i % 12) * 30  # 每小时 30°
            rad = math.radians(angle - 90)
            new_x = int(x + (r - 26) * math.cos(rad))
            new_y = int(y + (r - 26) * math.sin(rad))
            dsc = lv.draw_label_dsc_t()
            dsc.init()
            dsc.color = lv.color_hex(0xaaaaaa)
            dsc.font = lv.font_montserrat_16
            dsc.opa = lv.OPA.COVER
            dsc.flag = lv.TEXT_FLAG.FIT
            dsc.align = lv.TEXT_ALIGN.CENTER
            dsc.text = str(i)
            coords = lv.area_t()
            coords.x1 = new_x - 10
            coords.y1 = new_y - 8
            coords.x2 = new_x + 10
            coords.y2 = new_y + 2
            lv.draw_label(self.layer, dsc, coords)
        
        # 绘制指针
        now = utime.localtime()
        hour, minute, second = now[3], now[4], now[5]
        hour_angle = (hour % 12) * 30 + (minute / 2)
        minute_angle = minute * 6 + (second / 10)
        second_angle = second * 6
        self.clock_draw_needle(hour_angle, int(r * 0.5), 6, 0x999999, key)
        self.clock_draw_needle(minute_angle, int(r * 0.68), 4, 0xcccccc, key)
        self.clock_draw_needle(second_angle, int(r * 0.87), 3, 0xff6666, key)

        # 绘制指针原点
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(0xff6666)
        dsc.bg_opa = lv.OPA.COVER
        dsc.border_width = 0
        dsc.radius = 10
        coords = lv.area_t()
        coords.x1 = x - 6
        coords.y1 = y - 6
        coords.x2 = x + 6
        coords.y2 = y + 6
        lv.draw_rect(self.layer, dsc, coords)
    
    def clock_draw_needle(self, angle, length, width, color, key):
        x = self.clocks[key]['x']
        y = self.clocks[key]['y']
        rad = math.radians(angle - 90)
        x2 = int(x + length * math.cos(rad))
        y2 = int(y + length * math.sin(rad))
        dsc = lv.draw_line_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color)
        dsc.width = width
        dsc.opa = lv.OPA.COVER
        dsc.p1.x = x 
        dsc.p1.y = y
        dsc.p2.x = x2
        dsc.p2.y = y2
        lv.draw_line(self.layer, dsc)


class GUI_Widget(LV_GUI):
    def __init__(self, scr = None, group = None):
        super().__init__(scr, group if group != None else True )
        self.btns = {}
        self.textareas = {}
        self.labels = {}
        self.charts = {}
        self.tables = {}
        self.bars = {}
        self.scales = {}

    def btn_init(self, txt='btn 1', x=10, y=10, width=60, height=34, color=0xff0000, bg_color=0xffff00, cb=None, font=24, key='btn', args=None):
        if (key not in self.btns):
            self.btns[key] = lv.button(self.scr)
            self.btns[key].add_style(self.obj_sty, lv.PART.MAIN)
            self.btns[key].set_style_radius(6, lv.PART.MAIN)
            label = lv.label(self.btns[key])
            label.set_style_text_font(GUI_ATTR['font_size'].get(str(font)), lv.PART.MAIN)
            label.align(lv.ALIGN.CENTER, 0, 0)
            if cb: self.btns[key].add_event_cb(cb, lv.EVENT.CLICKED, args)
        self.btns[key].get_child(0).set_text(txt)
        self.btns[key].get_child(0).set_style_text_color(lv.color_hex(color), lv.PART.MAIN)
        self.btns[key].set_pos(x, y)
        self.btns[key].set_size(width, height)
        self.btns[key].set_style_bg_color(lv.color_hex(bg_color), lv.PART.MAIN)
        self.btns[key].move_foreground()
        self.group.add_obj(self.btns[key])

    def textarea_init(self, txt='textarea 1', x=10, y=10, width=200, height=45, mode=True, font=24, key='textarea'):
        if (key not in self.textareas):
            self.textareas[key] = lv.textarea(self.scr)
        self.textareas[key].set_pos(x, y)
        self.textareas[key].set_size(width, height)
        self.textareas[key].set_text(txt)
        self.textareas[key].set_one_line(mode)
        self.textareas[key].set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.textareas[key].set_style_text_font(GUI_ATTR['font_size'].get(str(font)), lv.PART.MAIN)
        self.textareas[key].move_foreground()
    
    def textarea_set_color(self, color=0x333333, bg_c=0xffffff, bd_c=0x333333, key='textarea'):
        if (key not in self.textareas):
            print('Textarea not initialized')
            return
        self.textareas[key].set_style_text_color(lv.color_hex(color), lv.PART.MAIN)
        self.textareas[key].set_style_bg_color(lv.color_hex(bg_c), lv.PART.MAIN)
        self.textareas[key].set_style_border_color(lv.color_hex(bd_c), lv.PART.MAIN)
    
    def textarea_set_txt(self, txt, key='textarea'):
        if (key not in self.textareas):
            print('Textarea not initialized')
            return
        self.textareas[key].set_text(txt)
    
    def label_init(self, txt='label 1', x=10, y=10, width=300, height=24, font_size=24, color=0xff0000, mode='clip', key='label'):
        if (key not in self.labels):
            self.labels[key] = lv.label(self.scr)
        self.labels[key].set_pos(x, y)
        self.labels[key].set_size(width, height)
        self.labels[key].set_text(txt)
        self.labels[key].set_style_text_color(lv.color_hex(color), lv.PART.MAIN)
        self.labels[key].set_style_text_font(GUI_ATTR['font_size'].get(str(font_size)), lv.PART.MAIN)
        self.labels[key].set_long_mode(GUI_ATTR['label_long_mode'].get(mode))
        self.labels[key].move_foreground()
    
    def label_set_txt(self, txt, color=0x333333, key='label'):
        if (key not in self.labels):
            print('Label not initialized')
            return
        self.labels[key].set_text(txt)
        self.labels[key].set_style_text_color(lv.color_hex(color), lv.PART.MAIN)

    def chart_init(self, x=10, y=5, width=300, height=162, serie_num=1, type='line', key='chart'):
        if (key not in self.charts):
            self.charts[key] = {}
            self.charts[key]['chart'] = lv.chart(self.scr)
            self.charts[key]['chart'].add_style(self.obj_sty, lv.PART.MAIN)
            self.charts[key]['chart'].set_type(GUI_ATTR['chart_type'].get(type))
            self.charts[key]['chart'].set_div_line_count(5, 7)
            self.charts[key]['chart'].set_point_count(7)
            self.charts['series'] = [None] * 4
            if serie_num > 0: self.charts['series'][0] = self.charts[key]['chart'].add_series(lv.palette_main(lv.PALETTE.GREEN), lv.chart.AXIS.PRIMARY_Y)
            if serie_num > 1: self.charts['series'][1] = self.charts[key]['chart'].add_series(lv.palette_main(lv.PALETTE.RED), lv.chart.AXIS.PRIMARY_Y)
            if serie_num > 2: self.charts['series'][2] = self.charts[key]['chart'].add_series(lv.palette_main(lv.PALETTE.BLUE), lv.chart.AXIS.PRIMARY_Y)
            if serie_num > 3: self.charts['series'][3] = self.charts[key]['chart'].add_series(lv.palette_main(lv.PALETTE.YELLOW), lv.chart.AXIS.PRIMARY_Y)
        self.charts[key]['chart'].set_pos(x, y)
        self.charts[key]['chart'].set_size(width, height)
        self.charts[key]['chart'].move_foreground()
    
    def chart_set_range(self, min, max, key):
        if (key not in self.charts):
            print('Chart not initialized')
            return
        self.charts[key]['chart'].set_range(lv.chart.AXIS.PRIMARY_Y, min, max)

    def chart_add_poit(self, serie, value, key):
        if (key not in self.charts):
            print('Chart not initialized')
            return
        if self.charts['series'][serie]:
            self.charts[key]['chart'].set_next_value(self.charts['series'][serie], value)
        else: print('Illegal serial number')

    def table_init(self, x=10, y=10, width=300, row=4, col=3, font=24, key='table'):
        if (key not in self.tables):
            self.tables[key] = lv.table(self.scr)
            cell_sty = lv.style_t()
            cell_sty.init()
            cell_sty.set_border_color(lv.color_hex(0x999999))
            cell_sty.set_border_width(1)
            cell_sty.set_border_side(lv.BORDER_SIDE.FULL)
            cell_sty.set_pad_top(4)
            cell_sty.set_pad_bottom(4)
            self.tables[key].add_style(cell_sty, lv.PART.ITEMS)
            self.tables[key].set_style_text_line_space(-10, lv.PART.MAIN)
        self.tables[key].set_pos(x, y)
        self.tables[key].set_row_count(row)
        self.tables[key].set_column_count(col)
        for i in range(col):
            self.tables[key].set_column_width(i, math.floor(width / col))
        self.tables[key].set_style_text_font(GUI_ATTR['font_size'].get(str(font)), lv.PART.MAIN)
        self.tables[key].move_foreground()
    
    def table_set_data(self, row_num, data=[], key='table'):
        if (key not in self.tables):
            print('Table not initialized')
            return
        if row_num <= 0:
            print('The number of rows should be greater than 0')
            return
        elif row_num > self.tables[key].get_row_count():
            return
        for i in range(len(data)):
            self.tables[key].set_cell_value(row_num - 1, i, data[i] if data[i] else '')

    def bar_init(self, x=10, y=10, width=60, height=34, key='bar'):
        if (key not in self.bars):
            self.bars[key] = lv.bar(self.scr)
        self.bars[key].set_pos(x, y)
        self.bars[key].set_size(width, height)
        self.bars[key].move_foreground()

    def bar_set_value(self, value=0, anim=False, key='bar'):
        if (key not in self.bars):
            print('Bar not initialized')
            return
        self.bars[key].set_value(value, GUI_ATTR['anim'].get('on' if anim else 'off'))

    def bar_set_range(self, min=0, max=100, key='bar'):
        if (key not in self.bars):
            print('Bar not initialized')
            return
        self.bars[key].set_range(min, max)
    
    def scale_init(self, x=10, y=10, width=152, height=152, mode='hor_bottom', needle_count=1, key='scale'):
        if (key not in self.scales):
            self.scales[key] = {}
            self.scales[key]['w'] = width
            self.scales[key]['h'] = height
            self.scales[key]['mode'] = mode
            self.scales[key]['scale'] = lv.scale(self.scr)
            self.scales[key]['scale'].set_pos(x, y)
            self.scales[key]['scale'].set_size(width, height)
            self.scales[key]['scale'].set_mode(GUI_ATTR['scale_mode'].get(mode))
            self.scales[key]['scale'].set_label_show(True)
            self.scales[key]['scale'].set_major_tick_every(5)
            self.scales[key]['scale'].set_total_tick_count(21)
            self.scales[key]['scale'].set_style_length(5, lv.PART.ITEMS)
            self.scales[key]['scale'].set_style_length(10, lv.PART.INDICATOR)
            if mode == 'hor_bottom': self.scale_set_mark_hor(needle_count, key)
            elif mode == 'ver_right': self.scale_set_mark_ver(needle_count, key)
            elif mode == 'round_inner': self.scale_set_needle(needle_count, key)
        else:
            self.scales[key]['w'] = width
            self.scales[key]['h'] = height
            self.scales[key]['scale'].set_pos(x, y)
            self.scales[key]['scale'].set_size(width, height)
        self.scales[key]['scale'].move_foreground()
    
    def scale_set_mark_hor(self, count, key):
        self.scales[key]['mark_hor'] = [None, None, None, None]
        color = [lv.palette_main(lv.PALETTE.RED), lv.palette_main(lv.PALETTE.GREEN), lv.palette_main(lv.PALETTE.BLUE), lv.palette_main(lv.PALETTE.YELLOW)]
        self.scales[key]['scale'].set_style_pad_top(24, lv.PART.MAIN)
        self.scales[key]['scale'].set_style_pad_hor(10, lv.PART.MAIN)
        for i in range(count):
            mark = lv.obj(self.scales[key]['scale'])
            mark.set_pos(-8, -22)
            mark.set_size(20, 20)
            mark.set_style_pad_all(0, lv.PART.MAIN)
            mark.set_style_radius(0, lv.PART.MAIN)
            mark.set_style_border_width(0, lv.PART.MAIN)
            mark.set_style_bg_opa(0, lv.PART.MAIN)

            line_sty = lv.style_t()
            line_sty.init()
            line_sty.set_line_width(2)
            line_sty.set_line_color(color[i])
            line_sty.set_line_rounded(True)

            line_points = [
                lv.point_precise_t({"x": 2, "y": 2}),
                lv.point_precise_t({"x": 9, "y": 18}),
                lv.point_precise_t({"x": 18, "y": 2}),
                lv.point_precise_t({"x": 2, "y": 2})
            ]
            line = lv.line(mark)
            line.set_points(line_points, len(line_points))
            line.add_style(line_sty, lv.PART.MAIN)
            self.scales[key]['mark_hor'][i] = mark
    
    def scale_set_mark_ver(self, count, key):
        h = self.scales[key]['h']
        self.scales[key]['mark_ver'] = [None, None, None, None]
        color = [lv.palette_main(lv.PALETTE.RED), lv.palette_main(lv.PALETTE.GREEN), lv.palette_main(lv.PALETTE.BLUE), lv.palette_main(lv.PALETTE.YELLOW)]
        self.scales[key]['scale'].set_style_pad_left(24, lv.PART.MAIN)
        self.scales[key]['scale'].set_style_pad_ver(10, lv.PART.MAIN)
        for i in range(count):
            mark = lv.obj(self.scales[key]['scale'])
            mark.set_pos(-22, h - 30)
            mark.set_size(20, 20)
            mark.set_style_pad_all(0, lv.PART.MAIN)
            mark.set_style_radius(0, lv.PART.MAIN)
            mark.set_style_border_width(0, lv.PART.MAIN)
            mark.set_style_bg_opa(0, lv.PART.MAIN)

            line_sty = lv.style_t()
            line_sty.init()
            line_sty.set_line_width(2)
            line_sty.set_line_color(color[i])
            line_sty.set_line_rounded(True)

            line_points = [
                lv.point_precise_t({"x": 2, "y": 2}),
                lv.point_precise_t({"x": 18, "y": 9}),
                lv.point_precise_t({"x": 2, "y": 18}),
                lv.point_precise_t({"x": 2, "y": 2})
            ]
            line = lv.line(mark)
            line.set_points(line_points, len(line_points))
            line.add_style(line_sty, lv.PART.MAIN)
            self.scales[key]['mark_ver'][i] = mark
    
    def scale_set_needle(self, count, key):
        w = self.scales[key]['w']
        h = self.scales[key]['h']
        self.scales[key]['needles'] = [None, None, None, None]
        color = [lv.palette_main(lv.PALETTE.RED), lv.palette_main(lv.PALETTE.GREEN), lv.palette_main(lv.PALETTE.BLUE), lv.palette_main(lv.PALETTE.YELLOW)]
        for i in range(count):
            needle = lv.line(self.scales[key]['scale'])
            needle.set_style_line_width(4, lv.PART.MAIN)
            needle.set_style_line_color(color[i], lv.PART.MAIN)
            needle.set_style_line_rounded(True, lv.PART.MAIN)
            self.scales[key]['scale'].set_line_needle_value(needle, math.floor(w / 2 * 0.8), 0)
            self.scales[key]['needles'][i] = needle

        point = lv.obj(self.scales[key]['scale'])
        point.set_size(10, 10)
        point.set_pos(math.floor(w / 2) - 5, math.floor(h / 2) - 5)
        point.add_style(self.obj_sty, lv.PART.MAIN)
        point.set_style_radius(5, lv.PART.MAIN)
        point.set_style_bg_color(lv.color_hex(0x333333), lv.PART.MAIN)
    
    def scale_set_value(self, needle=0, value=0, key='scale'):
        if (key not in self.scales):
            print('Scale not initialized')
            return
        w = self.scales[key]['w']
        h = self.scales[key]['h']
        mode = self.scales[key]['mode']
        min_sr = self.scales[key]['scale'].get_range_min_value()
        max_sr = self.scales[key]['scale'].get_range_max_value()
        if mode == 'hor_bottom':
            x = round((value - min_sr) / (max_sr - min_sr) * (w - 20)) - 8
            if self.scales[key]['mark_hor'][needle]: self.scales[key]['mark_hor'][needle].set_pos(x, -22)
        elif mode == 'ver_right':
            y = h - round((value - min_sr) / (max_sr - min_sr) * (h - 20)) - 30
            if self.scales[key]['mark_ver'][needle]: self.scales[key]['mark_ver'][needle].set_pos(-22, y)
        elif mode == 'round_inner':
            if self.scales[key]['needles'][needle]:
                self.scales[key]['scale'].set_line_needle_value(self.scales[key]['needles'][needle], math.floor(w / 2 * 0.8), value)
            
    def scale_set_range(self, min=0, max=100, color=0x0000ff, key='scale'):
        if (key not in self.scales):
            print('Scale not initialized')
            return
        self.scales[key]['scale'].set_range(min, max)
        self.scale_set_color(color, key)
    
    def scale_set_label(self, arr=[None], color=0x0000ff, key='scale'):
        if (key not in self.scales):
            print('Scale not initialized')
            return
        self.scales[key]['scale'].set_text_src(arr)
        self.scale_set_color(color, key)
    
    def scale_set_color(self, color=0x0000ff, key='scale'):
        if (key not in self.scales):
            print('Scale not initialized')
            return
        # 设置大刻度线和文本颜色
        label_sty = lv.style_t()
        label_sty.init()
        label_sty.set_text_font(lv.font_montserrat_16)
        label_sty.set_text_color(lv.color_hex(color))
        label_sty.set_line_color(lv.color_hex(color))
        label_sty.set_width(10)
        label_sty.set_line_width(2)
        self.scales[key]['scale'].add_style(label_sty, lv.PART.INDICATOR)
        # 设置小刻度线颜色
        minor_tick_sty = lv.style_t()
        minor_tick_sty.init()
        minor_tick_sty.set_line_color(lv.color_hex(color))
        minor_tick_sty.set_width(5)
        minor_tick_sty.set_line_width(2)
        self.scales[key]['scale'].add_style(minor_tick_sty, lv.PART.ITEMS)
        # 设置主轴线颜色
        main_line_sty = lv.style_t()
        main_line_sty.init()
        main_line_sty.set_line_color(lv.color_hex(color))
        main_line_sty.set_line_width(2)
        main_line_sty.set_arc_color(lv.color_hex(color))
        main_line_sty.set_arc_width(2)
        self.scales[key]['scale'].add_style(main_line_sty, lv.PART.MAIN)
    
    def scale_red_section(self, min=75, max=100, color=0xff0000, key='scale'):
        if (key not in self.scales):
            print('Scale not initialized')
            return
        # 设置红线区大刻度线和文本颜色
        label_sty = lv.style_t()
        label_sty.init()
        label_sty.set_text_font(lv.font_montserrat_16)
        label_sty.set_text_color(lv.color_hex(color))
        label_sty.set_line_color(lv.color_hex(color))
        label_sty.set_line_width(3)
        # 设置红线区小刻度线颜色
        minor_tick_sty = lv.style_t()
        minor_tick_sty.init()
        minor_tick_sty.set_line_color(lv.color_hex(color))
        minor_tick_sty.set_line_width(3)
        # 设置红线区主轴线颜色
        main_line_sty = lv.style_t()
        main_line_sty.init()
        main_line_sty.set_line_color(lv.color_hex(color))
        main_line_sty.set_line_width(3)
        main_line_sty.set_arc_color(lv.color_hex(color))
        main_line_sty.set_arc_width(3)
        # 获取红线区对象
        section = self.scales[key]['scale'].add_section()
        section.set_range(min, max)
        section.set_style(lv.PART.INDICATOR, label_sty)
        section.set_style(lv.PART.ITEMS, minor_tick_sty)
        section.set_style(lv.PART.MAIN, main_line_sty)


class GUI(CANVAS, GUI_Widget):
    def __init__(self):
        CANVAS.__init__(self)
        GUI_Widget.__init__(self)
        self.loop_event = event_loop(refresh_cb = self.refresh_loop_cb)
        
    def refresh_loop_cb(self):
        if self.loop_cb: self.loop_cb()

    def refresh_cb(self, loop_cb=None):
        if self.loop_event.is_running():
            self.loop_cb = loop_cb
        return self.loop_event

import time, math
import lvgl as lv
import lcd
import lv_displayer

from lv_utils import event_loop

# 是否为中文
def is_chinese_char(char):
    code = ord(char)
    return (
        # 中文汉字
        0x4E00 <= code <= 0x9FFF or    # 常用汉字
        0x3400 <= code <= 0x4DBF or    # 扩展A
        0x20000 <= code <= 0x2A6DF or  # 扩展B
        0x2A700 <= code <= 0x2B73F or  # 扩展C
        0x2B740 <= code <= 0x2B81F or  # 扩展D
        0x2B820 <= code <= 0x2CEAF or  # 扩展E
        0xF900 <= code <= 0xFAFF or    # 兼容汉字
        0x2F800 <= code <= 0x2FA1F or  # 兼容补充

        # 中文标点符号（CJK Symbols and Punctuation）
        0x3000 <= code <= 0x303F or    # 包括全角空格、。、《》、“”

        # 中文专用标点（如全角引号、破折号等）
        0xFF01 <= code <= 0xFF60       # 全角符号范围（！到～）
    )

# 自定义字符宽度
CUSTM_CHAR_WIDTH = {
    'a': 14, 'b': 15, 'c': 12, 'd': 15, 'e': 14, 'f': 8, 'g': 14, 'h': 15, 'i': 7, 'j': 7,
    'k': 14, 'l': 7, 'm': 23, 'n': 15, 'o': 15, 'p': 15, 'q': 15, 'r': 10, 's': 12, 't': 9,
    'u': 15, 'v': 13, 'w': 20, 'x': 13, 'y': 13, 'z': 12,
    'A': 15, 'B': 16, 'C': 15, 'D': 17, 'E': 14, 'F': 14, 'G': 17, 'H': 18, 'I': 7, 'J': 12,
    'K': 16, 'L': 13, 'M': 20, 'N': 18, 'O': 18, 'P': 16, 'Q': 18, 'R': 16, 'S': 14, 'T': 15,
    'U': 18, 'V': 15, 'W': 21, 'X': 14, 'Y': 13, 'Z': 14,
    '~': 14, '!': 8, '@': 23, '#': 14, '$': 14, '%': 23, '^': 14, '&': 17, '*': 12, '(': 9,
    ')': 9, '_': 14, '+': 14, '-': 9, '=': 14, '{': 9, '}': 9, '[': 9, ']': 9, ':': 7,
    ';': 7, '"': 12, '\'': 7, '|': 7, '\\': 9, '<': 14, '>': 14, ',': 7, '.': 7, '?': 12,
    '/': 9, ' ': 5,
}


GUI_ATTR = {
    "font_size": {
        "24": lv.font_siyuan_heiti_medium_24
    },
    "text_flag": {
        "none": lv.TEXT_FLAG.NONE,
        "break_all": lv.TEXT_FLAG.BREAK_ALL,
        "expand": lv.TEXT_FLAG.EXPAND,
        "fit": lv.TEXT_FLAG.FIT
    }
}


class OLED:
    def __init__(self):
        self.width = 320
        self.height = 172
        self.c_label_lh = 32
        self.bg_color = 0x000000
        self.scr = lv.screen_active()
        self.init_canvas()
        self.scr.set_scroll_dir(lv.DIR.NONE)
        # 调用event_loop心跳进程
        event_loop()
    
    def init_canvas(self):
        self.draw_buf = bytearray(self.width * self.height * 4)
        self.canvas = lv.canvas(self.scr)
        self.canvas.set_buffer(self.draw_buf, self.width, self.height, lv.COLOR_FORMAT.ARGB8888)
        self.canvas.center()
        self.canvas.fill_bg(lv.color_hex(self.bg_color), lv.OPA.COVER)
        self.layer = lv.layer_t()
        self.canvas.init_layer(self.layer)
    
    def fill(self, type=0):
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        color = self.bg_color
        if type: color = 0xffffff
        else: color = 0x000000
        dsc.bg_color = lv.color_hex(color)
        dsc.bg_opa = lv.OPA.COVER
        coords = lv.area_t()
        coords.x1 = 0
        coords.y1 = 0
        coords.x2 = 320
        coords.y2 = 172
        lv.draw_rect(self.layer, dsc, coords)
    
    def show(self):
        self.canvas.finish_layer(self.layer)
        time.sleep(0.02)
        lv.task_handler()

    def DispChar(self, text, x=10, y=10, type=1, wrap=False):
        color = 0xffffff
        bg_color = 0x000000
        if type == 2:
            color = 0x000000
            bg_color = 0xffffff
        width = 0
        height = self.c_label_lh
        for ch in text:
            custom_char = CUSTM_CHAR_WIDTH.get(ch)
            if custom_char: # 自定义字符宽度
                width = width + custom_char
                continue
            if is_chinese_char(ch): # 中文字符宽度
                width = width + 24
            elif ch.isdigit(): # 数字字符宽度
                width = width + 14
            else: # 其他字符宽度
                width = width + 14
        if wrap:
            remain_w = self.width - x
            row_num = math.ceil(width / remain_w)
            row_num = math.ceil((width + ((row_num - 1) * 24)) / remain_w) # 为了避免每行后面可能出现空白断行区
            height = row_num * self.c_label_lh
            width = remain_w
        # 绘制字符背景
        dsc = lv.draw_rect_dsc_t()
        dsc.init()
        dsc.bg_color = lv.color_hex(bg_color)
        dsc.bg_opa = lv.OPA.COVER
        dsc.border_width = 0
        dsc.radius = 0
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y + 6
        coords.x2 = width + x
        coords.y2 = height + y + 6
        lv.draw_rect(self.layer, dsc, coords)
        # 绘制字符
        dsc = lv.draw_label_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color)
        dsc.font = GUI_ATTR['font_size'].get(str(24))
        dsc.opa = lv.OPA.COVER
        dsc.flag = GUI_ATTR['text_flag'].get('break_all' if wrap else 'fit')
        dsc.line_space = -13
        dsc.text = text
        coords = lv.area_t()
        coords.x1 = x
        coords.y1 = y
        coords.x2 = x + width
        coords.y2 = y + height
        lv.draw_label(self.layer, dsc, coords)
    
    def Bitmap(self, x=10, y=10, width=None, height=None, path=''):
        if not path:
            raise Exception('The image address cannot be empty.')
        elif not path.lower().endswith('.png'):
            raise Exception('Can only support PNG format images.')
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

oled = OLED()



""" 
import 
使用示例

from lv_oled import oled

oled.fill(0)
# oled.DispChar('在Python中，判断一个文件是否是.png文件，可以从文件名后缀来判断。', 10, 0, 1, True)
# oled.DispChar("Hello World!", 10, 96, 2)
oled.Bitmap(10, 10, 200, 120, 'pic.png')
oled.show()

"""
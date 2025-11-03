import random
import lvgl as lv
from mpython import accelerometer
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False

# 画布大小
CANVAS_WIDTH = 320
CANVAS_HEIGHT = 172
canvas = None
layer = None

# 角色参数
player_width = 24
player_height = 24
player_x = 0
player_y = 0
velocity = 0
direction = 0

# 平台参数
platform_width = 50
platform_height = 14
trap_width = 50
trap_height = 14
platform_count = 5
platform_speed = 3  # 平台上移速度

# 游戏状态
game_over = True
platforms = []
game_score = 0
last_safe_platform = None # 记录上一次站立的平台

def gui_back_cb(e):
    if game_over:
        change_route('home', destroy)


def init_game():
    """ 初始化游戏状态 """
    global player_x, player_y, velocity, platforms, game_over, game_score, last_safe_platform, platform_speed
    game_over = False
    game_score = 0
    last_safe_platform = None
    platform_speed = 3

    # 生成平台
    platforms.clear()
    for i in range(platform_count):
        x = random.randint(0, CANVAS_WIDTH - platform_width)
        y = CANVAS_HEIGHT - (i + 1) * (CANVAS_HEIGHT // platform_count)
        is_trap = random.random() < 0.15  # 15% 概率生成陷阱平台
        platforms.append([x, y, is_trap, random.random()])

    # 角色初始位置在最低的普通平台上
    safe_platforms = [p for p in platforms if not p[2]]  # 过滤出普通平台
    if safe_platforms:
        player_x = safe_platforms[0][0] + platform_width // 2 - player_width // 2
        player_y = safe_platforms[0][1] - player_height
    else:
        player_x = platforms[0][0] + platform_width // 2 - player_width // 2
        player_y = platforms[0][1] - player_height

    velocity = 0

def draw_rect(x, y, w, h, color):
    dsc = lv.draw_rect_dsc_t()
    dsc.init()
    dsc.bg_color = lv.color_hex(color)
    dsc.border_width = 0
    dsc.outline_width = 0

    coords = lv.area_t()
    coords.x1 = x
    coords.y1 = y
    coords.x2 = x + w
    coords.y2 = y + h

    lv.draw_rect(layer, dsc, coords)
    canvas.finish_layer(layer)


def draw_text(x, y, w, h, txt, align = lv.TEXT_ALIGN.LEFT):
    dsc = lv.draw_label_dsc_t()
    dsc.init()
    dsc.color = lv.color_hex(0xFFFFFF)
    dsc.font = lv.font_siyuan_heiti_medium_24
    dsc.align = align
    dsc.opa = lv.OPA.COVER
    dsc.text = str(txt)
    coords = lv.area_t()
    coords.x1 = x
    coords.y1 = y
    coords.x2 = x + w
    coords.y2 = y + h
    lv.draw_label(layer, dsc, coords)
    canvas.finish_layer(layer)

def draw_game():
    """ 绘制游戏场景 """
    dsc = lv.draw_rect_dsc_t()
    dsc.init()
    dsc.bg_color = lv.color_hex(0x000000)
    dsc.border_width = 0
    dsc.outline_width = 0
    # 绘制矩形
    coords = lv.area_t()
    coords.x1 = 0
    coords.y1 = 0
    coords.x2 = 320
    coords.y2 = 172
    lv.draw_rect(layer, dsc, coords)
    canvas.finish_layer(layer)
    
    
    # 如果游戏结束，显示“Game Over”
    if game_over:
        draw_text(210, 10, 100, 24, game_score, lv.TEXT_ALIGN.RIGHT)
        draw_text(0, 50, 320, 50, 'GAME OVER', lv.TEXT_ALIGN.CENTER)
        draw_text(0, 94, 320, 24, '按下B键重新开始游戏', lv.TEXT_ALIGN.CENTER)
        draw_text(10, 0, 100, 24, 'A-返回')
        return
    
    # 绘制角色
    draw_rect(player_x, player_y, player_width, player_height, 0x00ff00)
    
    # 绘制平台
    for x, y, is_trap, key in platforms:
        color = 0x0000ff if not is_trap else 0xff0000
        height = platform_height if not is_trap else trap_height
        draw_rect(x, y, platform_width, height, color)
    
    draw_text(210, 10, 100, 24, game_score, lv.TEXT_ALIGN.RIGHT)


def update_game(timer):
    global player_x, player_y, velocity, platforms, game_over, game_score, last_safe_platform, direction, platform_speed

    if game_over:
        return  # 游戏结束时不再更新
    
    acc = accelerometer.get_y()
    if acc > 0.4:
        player_x = max(0, player_x - 10)
        direction = 0
    
    elif acc < -0.4:
        player_x = min(CANVAS_WIDTH - player_width, player_x + 10)
        direction = 1

    # 角色自由下落
    velocity += 1  # 模拟重力
    player_y += velocity
    
    # 记录是否落在新的普通平台上
    new_safe_platform = None

    # 检测平台碰撞
    for px, py, is_trap, key in platforms:
        platform_h = platform_height if not is_trap else trap_height

        # **改进的碰撞检测**
        if player_x + player_width >= px and player_x <= px + platform_width and \
           player_y + player_height >= py and player_y + player_height <= py + platform_h:
            if is_trap:
                game_over = True  # 角色踩到陷阱平台，游戏结束
            else:
                player_y = py - player_height  # 站在普通平台上
                velocity = 0  # 停止下落
                new_safe_platform = key  # 记录当前平台位置
    
    # **如果落到新普通平台，并且不是上一次的平台，则加分**
    if new_safe_platform and new_safe_platform != last_safe_platform:
        if last_safe_platform:
            game_score += 1
            if game_score % 20 == 0:
                platform_speed += 1
        last_safe_platform = new_safe_platform  # 记录本次成功站立的平台

    
    # **检查并重新生成超出屏幕的旧平台**
    min_vertical_gap = player_height # **最小垂直间距，确保至少一个角色高度**
    new_platforms = []
    
    for platform in platforms:
        platform[1] -= platform_speed
        if platform[1] < 0:  # 超出屏幕
            max_attempts = 20  # 限制尝试次数，防止死循环
            for _ in range(max_attempts):
                new_x = random.randint(0, CANVAS_WIDTH - platform_width)
                new_y = CANVAS_HEIGHT
                new_is_trap = random.random() < 0.15  # **陷阱平台概率（15%）**

                # **检查新平台是否与所有旧平台重叠**
                overlapping = any(abs(new_y - py) < min_vertical_gap for _, py, _, _ in platforms + new_platforms)

                if not overlapping:
                    new_platforms.append([new_x, new_y, new_is_trap, random.random()])
                    break  # 找到合适位置后跳出循环
        else:
            new_platforms.append(platform)

    platforms[:] = new_platforms  # 更新平台列表

    # 检查游戏是否结束
    if player_y < 0 or player_y > CANVAS_HEIGHT:
        game_over = True

    draw_game()

def restart_game():
    if game_over:
        init_game()
        draw_game()

def init():
    global container, timer_flag, canvas, layer
    timer_flag = True
    
    obj_sty = lv.style_t()
    obj_sty.init()
    obj_sty.set_pad_all(0)
    obj_sty.set_radius(0)
    obj_sty.set_border_width(0)
    
    container_sty = lv.style_t()
    container_sty.init()
    container_sty.set_size(lv.pct(100), lv.pct(100))
    container_sty.set_bg_color(lv.color_hex(0xE8E8E8))
    container_sty.set_pad_gap(0)

    
    container = lv.obj()
    container.add_style(obj_sty, lv.PART.MAIN)
    container.add_style(container_sty, lv.PART.MAIN)
    container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    draw_buf = bytearray(CANVAS_WIDTH * CANVAS_HEIGHT * 4)
    
    canvas = lv.canvas(container)
    canvas.set_buffer(draw_buf, CANVAS_WIDTH, CANVAS_HEIGHT, lv.COLOR_FORMAT.ARGB8888)
    canvas.center()
    canvas.fill_bg(lv.color_hex(0x000000), lv.OPA.COVER)
    
    layer = lv.layer_t()
    canvas.init_layer(layer)
    
    draw_text(0, 50, 320, 50, '是勇士就下100层', lv.TEXT_ALIGN.CENTER)
    draw_text(0, 94, 320, 24, '按下B键开始游戏', lv.TEXT_ALIGN.CENTER)
    draw_text(10, 0, 100, 24, 'A-返回')
    canvas.finish_layer(layer)
    
    # 创建定时器
    lv.timer_create(update_game, 50, None)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)

    set_key_config({
        'button_a_key_cb': lambda: back_btn.send_event(lv.EVENT.CLICKED, None),
        'button_b_key_cb': lambda: restart_game()
    })
    
    
def destroy():
    global container, timer_flag
    timer_flag = False
    container.clean()
    container = None
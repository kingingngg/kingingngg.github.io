#此版本增加了我的世界java版mojang工作室风格的进度条，并优化了墙壁纹理。
#以下是完整代码。
import pygame
import math
import random
import sys
from pygame.locals import *
import time

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 确保中文显示正常
pygame.font.init()
font_names = ['simsun', 'simhei', 'microsoftyahei', 'simkai', 'simsong']
font_path = None
for name in font_names:
    font_path = pygame.font.match_font(name)
    if font_path:
        break
if not font_path:
    font_path = pygame.font.get_default_font()

# 游戏设置
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("后室 - Backrooms")
clock = pygame.time.Clock()
FPS = 60

# 游戏状态常量
MENU = 0
MAP_SELECT = 1
GAME_PLAY = 2
OPTIONS = 3
QUIT = 4
LOADING = 5  # 新增加载状态

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
BACKROOMS_YELLOW = (200, 200, 180)
MINECRAFT_GREEN = (0, 166, 81)  # Minecraft风格的绿色


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.font.Font(font_path, font_size)
        self.active = True

    def draw(self, surface):
        # 检查鼠标是否悬停
        color = self.hover_color if self.is_hovered() and self.active else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)

        # 绘制文本
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_clicked(self, event):
        return self.active and event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered()


# 玩家类
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = math.pi / 2  # 初始视角方向
        self.speed = 5.0
        self.rotation_speed = 0.003


# 游戏类
def create_wall_texture(width, height):
    texture = pygame.Surface((width, height))
    base_color = BACKROOMS_YELLOW
    texture.fill(base_color)

    # 1. 基础纹理 - 轻微噪点
    for _ in range(width * height // 10):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color_variation = random.randint(-5, 5)
        color = (
            max(180, min(220, base_color[0] + color_variation)),
            max(180, min(220, base_color[1] + color_variation)),
            max(160, min(200, base_color[2] + color_variation))
        )
        pygame.draw.rect(texture, color, (x, y, 1, 1))

    # 2. 污渍效果 - 更多层次
    for _ in range(50):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(8, 30)
        color = (
            random.randint(140, 170),
            random.randint(140, 170),
            random.randint(120, 150)
        )
        # 不规则形状污渍
        for i in range(360):
            angle_rad = math.radians(i)
            radius = size * (0.5 + random.random() * 0.5)
            px = x + int(math.cos(angle_rad) * radius)
            py = y + int(math.sin(angle_rad) * radius)
            if 0 <= px < width and 0 <= py < height:
                pygame.draw.circle(texture, color, (px, py), 1)

    # 3. 霉斑效果 - 更自然的分布
    for _ in range(20):
        x = random.randint(0, width - 1)
        y = random.randint(height // 3, height - 1)  # 更多分布在下方
        size = random.randint(15, 50)
        color = (
            random.randint(40, 70),
            random.randint(70, 110),
            random.randint(40, 70)
        )
        # 不规则椭圆霉斑
        for i in range(int(size * 3)):
            ox = random.randint(-size, size)
            oy = random.randint(-size//2, size//2)
            if ox*ox/(size*size) + oy*oy/(size*size/4) < 1:  # 椭圆范围内
                px = x + ox
                py = y + oy
                if 0 <= px < width and 0 <= py < height:
                    pygame.draw.circle(texture, color, (px, py), 1)

    # 4. 纹理线条 - 更丰富的线条变化
    line_color = (180, 180, 160)
    # 水平线条 - 随机粗细和间隔
    y = 0
    while y < height:
        line_height = random.randint(1, 2)
        pygame.draw.line(texture, line_color, (0, y), (width, y), line_height)
        y += random.randint(15, 25)

    # 垂直线条 - 随机粗细和间隔
    x = 0
    while x < width:
        line_width = random.randint(1, 2)
        pygame.draw.line(texture, line_color, (x, 0), (x, height), line_width)
        x += random.randint(15, 25)

    # 5. 添加细小划痕
    for _ in range(100):
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        length = random.randint(5, 30)
        angle = random.uniform(0, math.pi * 2)
        end_x = start_x + int(math.cos(angle) * length)
        end_y = start_y + int(math.sin(angle) * length)
        end_x = max(0, min(width - 1, end_x))
        end_y = max(0, min(height - 1, end_y))
        # 划痕颜色略深
        scratch_color = (170, 170, 150)
        pygame.draw.line(texture, scratch_color, (start_x, start_y), (end_x, end_y), 1)

    # 6. 局部磨损效果
    for _ in range(10):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(20, 60)
        for i in range(size * size // 2):
            px = x + random.randint(-size//2, size//2)
            py = y + random.randint(-size//2, size//2)
            if 0 <= px < width and 0 <= py < height:
                if random.random() < 0.3:  # 磨损概率
                    wear_color = (
                        min(255, base_color[0] + random.randint(5, 15)),
                        min(255, base_color[1] + random.randint(5, 15)),
                        min(255, base_color[2] + random.randint(5, 15))
                    )
                    pygame.draw.rect(texture, wear_color, (px, py, 1, 1))

    return texture


def create_floor_texture(width, height):
    texture = pygame.Surface((width, height))
    texture.fill((100, 100, 90))

    # 添加地板纹理
    for x in range(0, width, 40):
        for y in range(0, height, 40):
            color = (random.randint(90, 110), random.randint(90, 110), random.randint(80, 100))
            pygame.draw.rect(texture, color, (x, y, 20, 20), 0)
            pygame.draw.rect(texture, color, (x + 20, y + 20, 20, 20), 0)

    return texture


def create_ceiling_texture(width, height):
    texture = pygame.Surface((width, height))
    texture.fill((180, 180, 160))

    # 添加天花板纹理和污渍
    for _ in range(50):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(3, 15)
        color = (random.randint(160, 170), random.randint(160, 170), random.randint(140, 150))
        pygame.draw.circle(texture, color, (x, y), size, 0)

    # 添加天花板线条
    for x in range(0, width, 60):
        pygame.draw.line(texture, (170, 170, 150), (x, 0), (x, height), 1)
    for y in range(0, height, 60):
        pygame.draw.line(texture, (170, 170, 150), (0, y), (width, y), 1)

    return texture


def create_ambient_sound():
    try:
        sample_rate = 44100
        duration = 2  # 2秒
        frequency = 60  # 低频

        n_samples = int(sample_rate * duration)
        buf = pygame.sndarray.array(pygame.mixer.Sound((sample_rate, -16, 1, n_samples, pygame.mixer.mono)))

        for i in range(n_samples):
            t = float(i) / sample_rate
            buf[i] = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))

        # 添加一些随机噪音
        for i in range(n_samples):
            buf[i] += int(random.uniform(-1000, 1000))
            buf[i] = max(-32768, min(32767, buf[i]))

        sound = pygame.sndarray.make_sound(buf)
        sound.set_volume(0.1)
        return sound
    except:
        print("无法创建环境音效")
        return None


def create_default_map():#初始地图
    return [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]


def draw_text(text, size, x, y, color=WHITE, center=False):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


class BackroomsGame:
    def __init__(self):
        self.paused = None
        self.pause_buttons = None
        self.ingame_buttons = None
        self.options_buttons = None
        self.map_buttons = None
        self.menu_buttons = None
        self.state = LOADING  # 初始状态改为LOADING
        self.player = Player(10.0, 10.0)
        self.map_size = 20
        self.game_map = create_default_map()
        self.fov = math.pi / 3
        self.half_fov = self.fov / 2
        self.num_rays = WIDTH // 2
        self.ray_step = self.fov / self.num_rays
        self.scale = WIDTH // self.num_rays

        # 加载进度相关变量
        self.loading_progress = 0
        self.loading_texts = [
            "初始化游戏引擎...",
            "加载纹理资源...",
            "生成游戏地图...",
            "初始化音效系统...",
            "准备渲染器...",
            "加载用户界面...",
            "启动游戏环境...",
            "奥利给!"
        ]
        self.current_loading_text = 0
        self.last_progress_update = 0
        self.progress_speed = 0.5  # 进度增加速度

        # 生成纹理
        self.wall_texture = create_wall_texture(256, 256)
        self.floor_texture = create_floor_texture(512, 512)
        self.ceiling_texture = create_ceiling_texture(512, 512)

        # 创建UI元素
        self.create_ui_elements()

        # 音效
        self.ambient_sound = create_ambient_sound()
        self.sound_on = True

        # 鼠标状态
        self.mouse_locked = False

    def create_ui_elements(self):
        # 主菜单按钮
        button_width = 200
        button_height = 50
        button_y = HEIGHT // 2 - 100
        button_spacing = 70

        self.menu_buttons = [
            Button(WIDTH // 2 - button_width // 2, button_y, button_width, button_height,
                   "开始游戏", BLUE, (0, 0, 255), WHITE),
            Button(WIDTH // 2 - button_width // 2, button_y + button_spacing, button_width, button_height,
                   "选择地图", BLUE, (0, 0, 255), WHITE),
            Button(WIDTH // 2 - button_width // 2, button_y + button_spacing * 2, button_width, button_height,
                   "设置", BLUE, (0, 0, 255), WHITE),
            Button(WIDTH // 2 - button_width // 2, button_y + button_spacing * 3, button_width, button_height,
                   "退出", RED, (255, 0, 0), WHITE)
        ]

        # 地图选择按钮
        map_button_width = 150
        map_button_height = 40
        map_start_x = WIDTH // 2 - 200
        map_start_y = HEIGHT // 2 - 100
        map_spacing = 60

        self.map_buttons = [
            Button(map_start_x, map_start_y, map_button_width, map_button_height,
                   "默认地图", BLUE, (0, 0, 255), WHITE),
            Button(map_start_x + 220, map_start_y, map_button_width, map_button_height,
                   "迷宫地图", BLUE, (0, 0, 255), WHITE),
            Button(map_start_x, map_start_y + map_spacing, map_button_width, map_button_height,
                   "大房间", BLUE, (0, 0, 255), WHITE),
            Button(map_start_x + 220, map_start_y + map_spacing, map_button_width, map_button_height,
                   "随机生成", BLUE, (0, 0, 255), WHITE),
            Button(WIDTH // 2 - map_button_width // 2, HEIGHT - 100, map_button_width, map_button_height,
                   "返回", GRAY, (150, 150, 150), WHITE)
        ]

        # 设置界面按钮
        options_button_width = 150
        options_button_height = 40

        self.options_buttons = [
            Button(WIDTH // 2 - options_button_width // 2, HEIGHT // 2 + 50, options_button_width,
                   options_button_height,
                   "音效: 开", GREEN, (0, 255, 0), WHITE),
            Button(WIDTH // 2 - options_button_width // 2, HEIGHT - 100, options_button_width, options_button_height,
                   "返回", GRAY, (150, 150, 150), WHITE)
        ]

        # 游戏中按钮
        self.ingame_buttons = [
            Button(WIDTH - 120, 20, 100, 40, "暂停", GRAY, (150, 150, 150), WHITE, 18)
        ]

        # 暂停菜单按钮
        self.pause_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "继续游戏", BLUE, (0, 0, 255), WHITE),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "返回主菜单", GRAY, (150, 150, 150), WHITE)
        ]

        self.paused = False

    # 创建纹理 - 优化后的墙壁纹理

    # 生成音效

    # 地图生成

    def create_maze_map(self, size=20):
        # 使用递归回溯法生成迷宫
        map = [[1 for _ in range(size)] for _ in range(size)]
        stack = []

        # 起始位置(必须是奇数)
        start_x, start_y = 1, 1
        map[start_y][start_x] = 0
        stack.append((start_x, start_y))

        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]

        while stack:
            x, y = stack[-1]
            neighbors = []

            # 检查所有方向的邻居
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if size - 1 > nx >= 1 == map[ny][nx] and 1 <= ny < size - 1:
                    neighbors.append((nx, ny))

            if neighbors:
                # 随机选择一个邻居
                nx, ny = random.choice(neighbors)
                map[ny][nx] = 0
                # 打通当前单元格和邻居之间的墙
                map[y + (ny - y) // 2][x + (nx - x) // 2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # 确保玩家有初始位置
        self.player.x, self.player.y = start_x + 0.5, start_y + 0.5
        return map

    def create_large_room_map(self, size=20):
        # 创建一个大房间，周围有墙，内部有少量障碍物
        map = [[1 for _ in range(size)] for _ in range(size)]

        # 填充内部为空地
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                map[y][x] = 0

        # 添加一些随机障碍物
        obstacle_count = size * size // 20
        for _ in range(obstacle_count):
            x = random.randint(2, size - 3)
            y = random.randint(2, size - 3)
            map[y][x] = 1

            # 确保障碍物不会完全阻挡路径
            if random.random() < 0.7:
                map[y + 1][x] = 1
            if random.random() < 0.7:
                map[y - 1][x] = 1
            if random.random() < 0.7:
                map[y][x + 1] = 1
            if random.random() < 0.7:
                map[y][x - 1] = 1

        # 设置玩家位置
        self.player.x, self.player.y = size // 2, size // 2
        return map

    def create_random_map(self, size=20, wall_density=0.3):
        # 创建随机地图
        map = [[1 for _ in range(size)] for _ in range(size)]

        # 填充大部分为空地
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                if random.random() > wall_density:
                    map[y][x] = 0

        # 确保玩家可以移动（简单的连通性检查）
        start_x, start_y = size // 2, size // 2
        map[start_y][start_x] = 0  # 确保起点是空地

        # 确保起点周围有空间
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if 1 <= start_x + dx < size - 1 and 1 <= start_y + dy < size - 1:
                    map[start_y + dy][start_x + dx] = 0

        self.player.x, self.player.y = start_x + 0.5, start_y + 0.5
        return map

    # 射线检测
    def cast_rays(self):
        rays = []
        start_angle = self.player.angle - self.half_fov
        min_distance = 0.1

        for ray in range(self.num_rays):
            angle = start_angle + ray * self.ray_step

            dx = math.cos(angle)
            dy = math.sin(angle)

            distance = min_distance
            max_distance = 20
            hit_found = False

            while distance < max_distance:
                x = self.player.x + dx * distance
                y = self.player.y + dy * distance

                map_x = int(x)
                map_y = int(y)

                if 0 <= map_x < self.map_size and 0 <= map_y < self.map_size:
                    if self.game_map[map_y][map_x] == 1:
                        hit_x = x - map_x
                        hit_y = y - map_y

                        if abs(dx) > abs(dy):
                            hit = hit_y
                            side = 0
                        else:
                            hit = hit_x
                            side = 1

                        corrected_distance = distance * math.cos(self.player.angle - angle)
                        corrected_distance = max(corrected_distance, min_distance)

                        rays.append((corrected_distance, angle, hit, side))
                        hit_found = True
                        break
                else:
                    break

                distance += 0.1

            if not hit_found:
                rays.append((max_distance, angle, 0, 0))

        return rays

    # 渲染场景
    def render_scene(self, rays):
        # 绘制天花板
        ceiling_scaled = pygame.transform.scale(self.ceiling_texture, (WIDTH, HEIGHT // 2))
        screen.blit(ceiling_scaled, (0, 0))

        # 绘制地板
        floor_scaled = pygame.transform.scale(self.floor_texture, (WIDTH, HEIGHT // 2))
        screen.blit(floor_scaled, (0, HEIGHT // 2))

        # 绘制墙壁
        for ray in range(self.num_rays):
            distance, angle, hit, side = rays[ray]

            if distance <= 0:
                distance = 0.1

            wall_height = min(int(HEIGHT / distance), HEIGHT * 2)

            tex_x = int(hit * self.wall_texture.get_width())
            if side == 0 and math.cos(angle) > 0:
                tex_x = self.wall_texture.get_width() - tex_x - 1
            if side == 1 and math.sin(angle) < 0:
                tex_x = self.wall_texture.get_width() - tex_x - 1

            wall_slice = self.wall_texture.subsurface(pygame.Rect(tex_x, 0, 1, self.wall_texture.get_height()))
            wall_slice = pygame.transform.scale(wall_slice, (self.scale, wall_height))

            # 墙壁亮度
            if side == 1:
                wall_slice.set_alpha(min(255, int(220 / (distance * 0.1))))
            else:
                wall_slice.set_alpha(min(255, int(250 / (distance * 0.1))))

            x = ray * self.scale
            y = (HEIGHT // 2) - (wall_height // 2)

            screen.blit(wall_slice, (x, y))

    # 绘制小地图
    def draw_minimap(self):
        minimap_size = 200
        cell_size = minimap_size // self.map_size
        minimap = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap.fill((0, 0, 0, 100))

        # 绘制地图
        for y in range(self.map_size):
            for x in range(self.map_size):
                if self.game_map[y][x] == 1:
                    pygame.draw.rect(minimap, GRAY, (x * cell_size, y * cell_size, cell_size - 1, cell_size - 1))

        # 绘制玩家
        player_minimap_x = int(self.player.x * cell_size)
        player_minimap_y = int(self.player.y * cell_size)
        pygame.draw.circle(minimap, YELLOW, (player_minimap_x, player_minimap_y), 5)

        # 绘制视线
        line_end_x = player_minimap_x + math.cos(self.player.angle) * 20
        line_end_y = player_minimap_y + math.sin(self.player.angle) * 20
        pygame.draw.line(minimap, YELLOW, (player_minimap_x, player_minimap_y), (line_end_x, line_end_y), 2)

        screen.blit(minimap, (10, 10))

    # 绘制文本

    # 新增：渲染加载界面
    def render_loading_screen(self):
        screen.fill(BLACK)

        # 绘制工作室名称 - 使用Minecraft风格的绿色
        draw_text("Oligive Studio", 48, WIDTH // 2, HEIGHT // 3, MINECRAFT_GREEN, center=True)

        # 绘制加载文本
        if self.current_loading_text < len(self.loading_texts):
            loading_text = self.loading_texts[self.current_loading_text]
            draw_text(loading_text, 24, WIDTH // 2, HEIGHT // 2, WHITE, center=True)

        # 绘制进度条背景
        progress_bar_width = WIDTH * 0.6
        progress_bar_height = 30
        progress_bar_x = (WIDTH - progress_bar_width) // 2
        progress_bar_y = HEIGHT * 2 // 3

        # 进度条边框
        pygame.draw.rect(screen, WHITE, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 2)

        # 进度条填充
        if self.loading_progress > 0:
            fill_width = int((progress_bar_width - 4) * self.loading_progress / 100)
            pygame.draw.rect(screen, MINECRAFT_GREEN,
                             (progress_bar_x + 2, progress_bar_y + 2, fill_width, progress_bar_height - 4))

        # 绘制百分比
        progress_text = f"{int(self.loading_progress)}%"
        draw_text(progress_text, 24, WIDTH // 2, progress_bar_y + progress_bar_height + 20, WHITE, center=True)

        # 绘制提示
        draw_text("正在准备您的后室体验...", 18, WIDTH // 2, HEIGHT - 50, LIGHT_GRAY, center=True)

    # 更新加载进度
    def update_loading(self):
        current_time = time.time()

        # 每0.1秒更新一次进度
        if current_time - self.last_progress_update > 0.1:
            self.last_progress_update = current_time

            # 增加进度
            self.loading_progress += self.progress_speed

            # 根据进度更新加载文本
            if self.loading_progress >= 12.5 and self.current_loading_text == 0:
                self.current_loading_text = 1
            elif self.loading_progress >= 25 and self.current_loading_text == 1:
                self.current_loading_text = 2
            elif self.loading_progress >= 37.5 and self.current_loading_text == 2:
                self.current_loading_text = 3
            elif self.loading_progress >= 50 and self.current_loading_text == 3:
                self.current_loading_text = 4
            elif self.loading_progress >= 62.5 and self.current_loading_text == 4:
                self.current_loading_text = 5
            elif self.loading_progress >= 75 and self.current_loading_text == 5:
                self.current_loading_text = 6
            elif self.loading_progress >= 87.5 and self.current_loading_text == 6:
                self.current_loading_text = 7

            # 如果进度完成，切换到主菜单
            if self.loading_progress >= 100:
                self.state = MENU

    # 渲染主菜单
    def render_menu(self):
        screen.fill(BLACK)

        # 标题
        draw_text("后室", 72, WIDTH // 2, HEIGHT // 4, WHITE, center=True)
        draw_text("Backrooms", 36, WIDTH // 2, HEIGHT // 4 + 80, WHITE, center=True)

        # 绘制按钮
        for button in self.menu_buttons:
            button.draw(screen)

    # 渲染地图选择界面
    def render_map_select(self):
        screen.fill(BLACK)

        draw_text("选择地图", 48, WIDTH // 2, HEIGHT // 4, WHITE, center=True)

        for button in self.map_buttons:
            button.draw(screen)

    # 渲染设置界面
    def render_options(self):
        screen.fill(BLACK)

        draw_text("设置", 48, WIDTH // 2, HEIGHT // 4, WHITE, center=True)
        draw_text("音效", 24, WIDTH // 2 - 100, HEIGHT // 2 - 20, WHITE)

        for button in self.options_buttons:
            button.draw(screen)

    # 渲染游戏界面
    def render_game(self):
        # 绘制3D场景
        rays = self.cast_rays()
        self.render_scene(rays)

        # 绘制小地图
        self.draw_minimap()

        # 绘制信息
        draw_text("后室 - Backrooms", 24, 10, HEIGHT - 40)
        draw_text(f"位置: X={self.player.x:.1f}, Y={self.player.y:.1f}", 18, 10, HEIGHT - 20)
        draw_text("控制: WASD移动, 鼠标转向, Tab显示鼠标, ESC退出", 16, WIDTH - 350, 10)

        # 绘制游戏中按钮
        for button in self.ingame_buttons:
            button.draw(screen)

    # 渲染暂停界面
    def render_pause(self):
        # 半透明覆盖层
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text("游戏暂停", 48, WIDTH // 2, HEIGHT // 4, WHITE, center=True)

        for button in self.pause_buttons:
            button.draw(screen)

    # 处理事件
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = QUIT

            elif self.state == MENU:
                if self.menu_buttons[0].is_clicked(event):  # 开始游戏
                    self.state = GAME_PLAY
                    self.paused = False
                    self.mouse_locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    if self.sound_on and self.ambient_sound:
                        self.ambient_sound.play(-1)
                elif self.menu_buttons[1].is_clicked(event):  # 选择地图
                    self.state = MAP_SELECT
                elif self.menu_buttons[2].is_clicked(event):  # 设置
                    self.state = OPTIONS
                elif self.menu_buttons[3].is_clicked(event):  # 退出
                    self.state = QUIT

            elif self.state == MAP_SELECT:
                if self.map_buttons[0].is_clicked(event):  # 默认地图
                    self.game_map = create_default_map()
                    self.player.x, self.player.y = 10.0, 10.0
                    self.state = GAME_PLAY
                    self.paused = False
                    self.mouse_locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    if self.sound_on and self.ambient_sound:
                        self.ambient_sound.play(-1)
                elif self.map_buttons[1].is_clicked(event):  # 迷宫地图
                    self.game_map = self.create_maze_map()
                    self.state = GAME_PLAY
                    self.paused = False
                    self.mouse_locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    if self.sound_on and self.ambient_sound:
                        self.ambient_sound.play(-1)
                elif self.map_buttons[2].is_clicked(event):  # 大房间
                    self.game_map = self.create_large_room_map()
                    self.state = GAME_PLAY
                    self.paused = False
                    self.mouse_locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    if self.sound_on and self.ambient_sound:
                        self.ambient_sound.play(-1)
                elif self.map_buttons[3].is_clicked(event):  # 随机生成
                    self.game_map = self.create_random_map()
                    self.state = GAME_PLAY
                    self.paused = False
                    self.mouse_locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    if self.sound_on and self.ambient_sound:
                        self.ambient_sound.play(-1)
                elif self.map_buttons[4].is_clicked(event):  # 返回
                    self.state = MENU

            elif self.state == OPTIONS:
                if self.options_buttons[0].is_clicked(event):  # 音效开关
                    self.sound_on = not self.sound_on
                    if self.sound_on:
                        self.options_buttons[0].text = "音效: 开"
                        self.options_buttons[0].color = GREEN
                        self.options_buttons[0].hover_color = (0, 255, 0)
                        if self.ambient_sound:
                            self.ambient_sound.unpause()
                    else:
                        self.options_buttons[0].text = "音效: 关"
                        self.options_buttons[0].color = RED
                        self.options_buttons[0].hover_color = (255, 0, 0)
                        if self.ambient_sound:
                            self.ambient_sound.pause()
                elif self.options_buttons[1].is_clicked(event):  # 返回
                    self.state = MENU

            elif self.state == GAME_PLAY:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.paused = not self.paused
                        self.mouse_locked = not self.paused
                        pygame.mouse.set_visible(not self.mouse_locked)
                        pygame.event.set_grab(self.mouse_locked)
                    elif event.key == K_TAB:
                        self.mouse_locked = not self.mouse_locked
                        pygame.mouse.set_visible(not self.mouse_locked)
                        pygame.event.set_grab(self.mouse_locked)

                if self.ingame_buttons[0].is_clicked(event):  # 暂停按钮
                    self.paused = True
                    self.mouse_locked = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)

                if self.paused:
                    if self.pause_buttons[0].is_clicked(event):  # 继续游戏
                        self.paused = False
                        self.mouse_locked = True
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    elif self.pause_buttons[1].is_clicked(event):  # 返回主菜单
                        self.state = MENU
                        self.paused = False
                        if self.ambient_sound:
                            self.ambient_sound.stop()

    # 更新游戏状态
    def update(self):
        if self.state == LOADING:
            self.update_loading()
        elif self.state == GAME_PLAY and not self.paused and self.mouse_locked:
            # 鼠标移动控制视角
            mouse_dx, _ = pygame.mouse.get_rel()
            self.player.angle += mouse_dx * self.player.rotation_speed

            # 键盘移动控制
            keys = pygame.key.get_pressed()
            speed = self.player.speed * (1 / FPS)

            dx = math.cos(self.player.angle) * speed
            dy = math.sin(self.player.angle) * speed
            dx_side = math.cos(self.player.angle + math.pi / 2) * speed
            dy_side = math.sin(self.player.angle + math.pi / 2) * speed

            new_x, new_y = self.player.x, self.player.y

            if keys[K_w]:
                new_x += dx
                new_y += dy
            if keys[K_s]:
                new_x -= dx
                new_y -= dy
            if keys[K_a]:
                new_x += dx_side
                new_y += dy_side
            if keys[K_d]:
                new_x -= dx_side
                new_y -= dy_side

            # 碰撞检测
            if 1 <= int(new_x) < self.map_size - 1 and 1 <= int(new_y) < self.map_size - 1:
                if self.game_map[int(new_y)][int(new_x)] == 0:
                    self.player.x, self.player.y = new_x, new_y

    # 渲染当前状态
    def render(self):
        if self.state == LOADING:
            self.render_loading_screen()
        elif self.state == MENU:
            self.render_menu()
        elif self.state == MAP_SELECT:
            self.render_map_select()
        elif self.state == OPTIONS:
            self.render_options()
        elif self.state == GAME_PLAY:
            self.render_game()
            if self.paused:
                self.render_pause()

        pygame.display.flip()

    # 游戏主循环
    def run(self):
        while self.state != QUIT:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# 启动游戏
if __name__ == "__main__":
    game = BackroomsGame()
    game.run()
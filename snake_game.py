import pygame
import sys
import random
import json
import os
import math

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("可升级贪吃蛇游戏")

# 字体
pygame.font.init()
FONT_L = pygame.font.SysFont("Arial", 64, bold=True)
FONT_M = pygame.font.SysFont("Arial", 36, bold=True)
FONT_S = pygame.font.SysFont("Arial", 24)

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (40, 40, 40)

# 背景设置
GRID_SIZE = 20

# Trail settings
TRAIL_LENGTH = 10
TRAIL_COLOR = (0, 255, 0)  # Green trail

# 升级系统设置
LEVEL_THRESHOLDS = [0, 5, 10, 20]  # 积分阈值对应等级
SNAKE_SKINS = [
    {"color": WHITE, "glow": (200, 200, 200)},
    {"color": GREEN, "glow": (100, 255, 100)},
    {"color": BLUE, "glow": (100, 100, 255)},
    {"color": RED, "glow": (255, 100, 100)}
]  # 对应等级的皮肤颜色和发光效果
SNAKE_NAMES = ["蛇宝宝", "小蛇", "大蛇", "大蛇丸"]  # 对应等级的名称

# 游戏网格
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BLOCK_SIZE = GRID_SIZE

# 社交系统设置
ACHIEVEMENTS = {
    "first_food": {"name": "第一个食物", "condition": lambda s: s.score >= 1},
    "level_up": {"name": "首次升级", "condition": lambda s: s.level >= 1},
    "high_score": {"name": "高分达人", "condition": lambda s: s.score >= 20}
}
DATA_FILE = "game_data.json"

# 食物类型设置
FOOD_TYPES = {
    1: {'value': 1},
    2: {'value': 2},
    3: {'value': 3},
}

# 游戏状态
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_DIFFICULTY = "difficulty"
STATE_LEADERBOARD = "leaderboard"
STATE_GAME_OVER = "game_over"

# 难度
DIFFICULTIES = [
    {"name": "简单", "speed": 8},
    {"name": "普通", "speed": 12},
    {"name": "困难", "speed": 16},
    {"name": "地狱", "speed": 22},
]

# 星空粒子系统
class StarField:
    def __init__(self, num_stars=150):
        self.stars = []
        for _ in range(num_stars):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.uniform(0.5, 3.0),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.01, 0.05),
                'twinkle_offset': random.uniform(0, 2 * math.pi)
            })
    
    def update(self):
        for star in self.stars:
            star['twinkle_offset'] += star['twinkle_speed']
    
    def draw(self, surface):
        for star in self.stars:
            # 闪烁效果
            twinkle = 0.7 + 0.3 * math.sin(star['twinkle_offset'])
            brightness = int(star['brightness'] * twinkle * 255)
            color = (brightness, brightness, brightness)
            
            # 绘制星星
            if star['size'] > 2:
                # 大星星画十字形
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), int(star['size']))
                pygame.draw.line(surface, color, 
                               (star['x'] - star['size'] * 2, star['y']), 
                               (star['x'] + star['size'] * 2, star['y']), 2)
                pygame.draw.line(surface, color, 
                               (star['x'], star['y'] - star['size'] * 2), 
                               (star['x'], star['y'] + star['size'] * 2), 2)
            else:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), max(1, int(star['size'])))

# 粒子系统
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color, velocity, life=60):
        self.particles.append({
            'x': x, 'y': y,
            'vx': velocity[0], 'vy': velocity[1],
            'color': color,
            'life': life,
            'max_life': life,
            'size': random.uniform(1, 3)
        })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vy'] += 0.1  # 重力
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            # 创建带透明度的表面
            particle_surf = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, 
                             (int(particle['size']), int(particle['size'])), 
                             int(particle['size']))
            surface.blit(particle_surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))

def draw_background(surface):
    # 深空渐变背景
    for y in range(SCREEN_HEIGHT):
        # 从深蓝到黑色的渐变
        ratio = y / SCREEN_HEIGHT
        r = int(5 * (1 - ratio))
        g = int(10 * (1 - ratio))
        b = int(25 * (1 - ratio))
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # 绘制星空
    star_field.update()
    star_field.draw(surface)
    
    # 绘制精美网格
    grid_alpha = 15
    grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # 主网格线
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(grid_surf, (40, 60, 80, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(grid_surf, (40, 60, 80, grid_alpha), (0, y), (SCREEN_WIDTH, y))
    
    # 每5格一条加粗线
    for x in range(0, SCREEN_WIDTH, GRID_SIZE * 5):
        pygame.draw.line(grid_surf, (60, 80, 100, grid_alpha * 2), (x, 0), (x, SCREEN_HEIGHT), 2)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE * 5):
        pygame.draw.line(grid_surf, (60, 80, 100, grid_alpha * 2), (0, y), (SCREEN_WIDTH, y), 2)
    
    surface.blit(grid_surf, (0, 0))
    
    # 边框发光效果
    border_glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(5):
        alpha = 20 - i * 3
        color = (0, 100, 200, alpha)
        pygame.draw.rect(border_glow, color, (i, i, SCREEN_WIDTH - i * 2, SCREEN_HEIGHT - i * 2), 1)
    surface.blit(border_glow, (0, 0))

def draw_gradient_text(surface, text, font, colors, x, y):
    """绘制渐变文字"""
    text_surface = font.render(text, True, colors[0])
    text_rect = text_surface.get_rect()
    
    # 创建渐变效果
    gradient_surf = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
    
    for i in range(text_rect.height):
        ratio = i / text_rect.height
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        pygame.draw.line(gradient_surf, (r, g, b), (0, i), (text_rect.width, i))
    
    # 应用文字遮罩
    text_mask = pygame.mask.from_surface(text_surface)
    gradient_surf = text_mask.to_surface(gradient_surf, unsetcolor=(0, 0, 0, 0))
    
    surface.blit(gradient_surf, (x, y))
    return text_rect

# 蛇类
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
        self.score = 0
        self.level = 0
        self.achievements = []
        self.trail = []
        self.animation_offset = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 1

    def reset(self):
        self.__init__()

    def move(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self.grow:
            tail = self.body.pop()
            # 添加尾部粒子效果
            if len(self.body) > 3:
                particle_system.add_particle(
                    tail[0] * GRID_SIZE + GRID_SIZE // 2,
                    tail[1] * GRID_SIZE + GRID_SIZE // 2,
                    self.get_skin()["color"],
                    (random.uniform(-1, 1), random.uniform(-1, 1)),
                    30
                )
        else:
            self.grow = False

    def grow_snake(self):
        self.grow = True

    def change_direction(self, new_direction):
        if (new_direction[0] != -self.direction[0] or new_direction[1] != -self.direction[1]):
            self.direction = new_direction

    def check_collision(self):
        head = self.body[0]
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        if head in self.body[1:]:
            return True
        return False

    def eat_food(self, food_value):
        self.grow_snake()
        self.score += food_value
        self.update_level()
        
        # 吃食物时的粒子爆炸效果
        head = self.body[0]
        for _ in range(15):
            particle_system.add_particle(
                head[0] * GRID_SIZE + GRID_SIZE // 2,
                head[1] * GRID_SIZE + GRID_SIZE // 2,
                (255, 255, 100),
                (random.uniform(-3, 3), random.uniform(-3, 3)),
                45
            )

    def update_level(self):
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if self.score >= threshold:
                self.level = i
        pygame.display.set_caption(f"可升级贪吃蛇游戏 - {SNAKE_NAMES[self.level]}")

    def get_skin(self):
        return SNAKE_SKINS[self.level]

    def check_achievements(self):
        for key, ach in ACHIEVEMENTS.items():
            if key not in self.achievements and ach["condition"](self):
                self.achievements.append(key)

    def update(self):
        # Add trail
        if len(self.body) > 1:
            self.trail.append(self.body[-1])
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)
        
        # Update animation
        self.animation_offset += 0.1
        self.pulse_scale += 0.01 * self.pulse_direction
        if self.pulse_scale > 1.2 or self.pulse_scale < 0.8:
            self.pulse_direction *= -1

    def draw_3d_block(self, screen, x, y, color, glow_color, scale=1.0):
        block_size = int(BLOCK_SIZE * scale)
        rect = pygame.Rect(x, y, block_size, block_size)
        glow_size = block_size + 10
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_alpha = 50
        pygame.draw.circle(glow_surf, (*glow_color, glow_alpha), (glow_size//2, glow_size//2), glow_size//2)
        screen.blit(glow_surf, (x - (glow_size - block_size)//2, y - (glow_size - block_size)//2))
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        pygame.draw.rect(screen, self.lighten_color(color), highlight_rect)
        pygame.draw.rect(screen, color, rect)
        shadow_rect = pygame.Rect(rect.right - 4, rect.y + 4, 4, rect.height - 4)
        pygame.draw.rect(screen, self.darken_color(color), shadow_rect)
        bottom_shadow = pygame.Rect(rect.x + 4, rect.bottom - 4, rect.width - 4, 4)
        pygame.draw.rect(screen, self.darken_color(color), bottom_shadow)
        pygame.draw.rect(screen, self.darken_color(color), rect, 2)

    def lighten_color(self, color):
        return tuple(min(255, c + 30) for c in color)

    def darken_color(self, color):
        return tuple(max(0, c - 30) for c in color)

    def draw(self, screen):
        # trail
        for i, pos in enumerate(self.trail):
            alpha = int(128 * (1 - i / TRAIL_LENGTH))
            trail_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            trail_color = (*TRAIL_COLOR, alpha)
            pygame.draw.rect(trail_surf, trail_color, (0, 0, BLOCK_SIZE, BLOCK_SIZE))
            glow_surf = pygame.Surface((BLOCK_SIZE + 4, BLOCK_SIZE + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*TRAIL_COLOR, alpha//2), (BLOCK_SIZE//2 + 2, BLOCK_SIZE//2 + 2), BLOCK_SIZE//2 + 2)
            screen.blit(glow_surf, (pos[0] * BLOCK_SIZE - 2, pos[1] * BLOCK_SIZE - 2))
            screen.blit(trail_surf, (pos[0] * BLOCK_SIZE, pos[1] * BLOCK_SIZE))

        # body
        skin = self.get_skin()
        for i, block in enumerate(self.body):
            x = block[0] * BLOCK_SIZE
            y = block[1] * BLOCK_SIZE
            if i == 0:
                head_glow = pygame.Surface((BLOCK_SIZE + 8, BLOCK_SIZE + 8), pygame.SRCALPHA)
                glow_alpha = int(100 + 50 * math.sin(self.animation_offset * 3))
                pygame.draw.circle(head_glow, (*skin["glow"], glow_alpha), (BLOCK_SIZE//2 + 4, BLOCK_SIZE//2 + 4), BLOCK_SIZE//2 + 4)
                screen.blit(head_glow, (x - 4, y - 4))
                self.draw_3d_block(screen, x, y, skin["color"], skin["glow"], self.pulse_scale)
                eye_size = 3
                eye_offset = BLOCK_SIZE // 4
                pygame.draw.circle(screen, BLACK, (x + eye_offset, y + eye_offset), eye_size)
                pygame.draw.circle(screen, BLACK, (x + BLOCK_SIZE - eye_offset, y + eye_offset), eye_size)
                pygame.draw.circle(screen, WHITE, (x + eye_offset, y + eye_offset), 1)
                pygame.draw.circle(screen, WHITE, (x + BLOCK_SIZE - eye_offset, y + eye_offset), 1)
            else:
                body_alpha = 255 - (i * 10)
                body_color = (*skin["color"], max(100, body_alpha))
                body_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(body_surf, body_color, (0, 0, BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
                screen.blit(body_surf, (x, y))
                pygame.draw.rect(screen, self.darken_color(skin["color"]), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1, border_radius=3)

class Food:
    def __init__(self, level):
        self.position = self.random_position()
        self.type = min(level + 1, len(FOOD_TYPES))
        self.value = FOOD_TYPES[self.type]['value']
        self.animation_offset = random.uniform(0, 2 * math.pi)

    def random_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, screen):
        x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        float_y = y + 3 * math.sin(pygame.time.get_ticks() * 0.005 + self.animation_offset)
        if self.type == 1:
            radius = GRID_SIZE // 2 - 2
            glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 100, 100, 50), (radius * 3 // 2, radius * 3 // 2), radius * 3 // 2)
            screen.blit(glow_surf, (x - radius * 3 // 2, float_y - radius * 3 // 2))
            pygame.draw.circle(screen, RED, (x, int(float_y)), radius)
            pygame.draw.circle(screen, (255, 150, 150), (x - 3, int(float_y) - 3), radius // 3)
            pygame.draw.line(screen, GREEN, (x, int(float_y) - radius), (x, int(float_y) - radius - 4), 2)
        elif self.type == 2:
            radius = GRID_SIZE // 2 - 2
            glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, 60), (radius * 3 // 2, radius * 3 // 2), radius * 3 // 2)
            screen.blit(glow_surf, (x - radius * 3 // 2, float_y - radius * 3 // 2))
            pygame.draw.circle(screen, YELLOW, (x, int(float_y)), radius)
            pygame.draw.circle(screen, (255, 255, 150), (x - 3, int(float_y) - 3), radius // 3)
            pygame.draw.line(screen, GREEN, (x, int(float_y) - radius), (x, int(float_y) - radius - 4), 2)
        elif self.type == 3:
            points = [(x, int(float_y) - 8), (x + 8, int(float_y)), (x, int(float_y) + 8), (x - 8, int(float_y))]
            glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surf, (100, 100, 255, 80), [(12, 0), (24, 12), (12, 24), (0, 12)])
            screen.blit(glow_surf, (x - 12, int(float_y) - 12))
            pygame.draw.polygon(screen, BLUE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            sparkle_alpha = int(100 + 100 * math.sin(pygame.time.get_ticks() * 0.01))
            sparkle_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surf, (255, 255, 255, sparkle_alpha), (8, 8), 3)
            screen.blit(sparkle_surf, (x - 8, int(float_y) - 8))

# 加载/保存 数据
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"high_scores": [], "honors": []}

def save_data(data, score, achievements):
    data["high_scores"].append(score)
    data["high_scores"] = sorted(data["high_scores"], reverse=True)[:10]
    data["honors"].extend([ACHIEVEMENTS[ach]["name"] for ach in achievements if ACHIEVEMENTS[ach]["name"] not in data["honors"]])
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# UI 工具
def draw_text_center(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    x = (SCREEN_WIDTH - rendered.get_width()) // 2
    surface.blit(rendered, (x, y))

def draw_glowing_text(surface, text, font, color, glow_color, x, y):
    """绘制发光文字"""
    # 绘制发光效果
    for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2), (0, 2), (0, -2), (2, 0), (-2, 0)]:
        glow_surface = font.render(text, True, glow_color)
        surface.blit(glow_surface, (x + offset[0], y + offset[1]))
    
    # 绘制主文字
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

# 初始化全局对象
snake = Snake()
food = None
clock = pygame.time.Clock()
game_data = load_data()
star_field = StarField()
particle_system = ParticleSystem()

# 游戏流程状态
state = STATE_MENU
menu_items = ["开始游戏", "选择难度", "排行榜", "退出"]
menu_index = 0
menu_animation_time = 0

difficulty_index = 1  # 默认普通
current_speed = DIFFICULTIES[difficulty_index]["speed"]

# 主循环
running = True
saved_in_this_run = False

while running:
    if state == STATE_MENU:
        menu_animation_time += 0.05
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    menu_index = (menu_index - 1) % len(menu_items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    menu_index = (menu_index + 1) % len(menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = menu_items[menu_index]
                    if choice == "开始游戏":
                        snake.reset()
                        food = Food(snake.level)
                        saved_in_this_run = False
                        state = STATE_PLAY
                    elif choice == "选择难度":
                        state = STATE_DIFFICULTY
                    elif choice == "排行榜":
                        state = STATE_LEADERBOARD
                    elif choice == "退出":
                        running = False
        
        # 绘制菜单
        draw_background(screen)
        
        # 标题动画效果
        title_y = 80 + 10 * math.sin(menu_animation_time)
        draw_glowing_text(screen, "贪吃蛇", FONT_L, (255, 255, 255), (100, 150, 255), 
                         (SCREEN_WIDTH - FONT_L.size("贪吃蛇")[0]) // 2, int(title_y))
        
        # 副标题
        subtitle_colors = [(100, 200, 255), (200, 100, 255)]
        draw_gradient_text(screen, f"当前难度：{DIFFICULTIES[difficulty_index]['name']}", FONT_S, 
                          subtitle_colors, (SCREEN_WIDTH - FONT_S.size(f"当前难度：{DIFFICULTIES[difficulty_index]['name']}")[0]) // 2, 160)
        
        # 菜单项
        start_y = 230
        for i, item in enumerate(menu_items):
            item_y = start_y + i * 60
            if i == menu_index:
                # 选中项的动画效果
                pulse = 1.0 + 0.1 * math.sin(menu_animation_time * 3)
                glow_alpha = int(100 + 50 * math.sin(menu_animation_time * 2))
                
                # 绘制选中背景
                bg_surf = pygame.Surface((300, 50), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (50, 100, 200, 30), (0, 0, 300, 50), border_radius=10)
                screen.blit(bg_surf, ((SCREEN_WIDTH - 300) // 2, item_y - 10))
                
                # 绘制发光文字
                draw_glowing_text(screen, f"▶ {item}", FONT_M, (255, 255, 255), 
                                (100, 150, 255, glow_alpha), 
                                (SCREEN_WIDTH - FONT_M.size(f"▶ {item}")[0]) // 2, item_y)
            else:
                draw_text_center(screen, item, FONT_M, (180, 200, 220), item_y)
        
        pygame.display.flip()
        clock.tick(60)

    elif state == STATE_DIFFICULTY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    difficulty_index = (difficulty_index - 1) % len(DIFFICULTIES)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    difficulty_index = (difficulty_index + 1) % len(DIFFICULTIES)
                elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    current_speed = DIFFICULTIES[difficulty_index]["speed"]
                    state = STATE_MENU
        
        draw_background(screen)
        draw_glowing_text(screen, "选择难度", FONT_L, (255, 255, 255), (100, 150, 255),
                         (SCREEN_WIDTH - FONT_L.size("选择难度")[0]) // 2, 100)
        
        name = DIFFICULTIES[difficulty_index]["name"]
        speed = DIFFICULTIES[difficulty_index]["speed"]
        difficulty_text = f"{name} (速度: {speed} FPS)"
        
        # 难度显示带颜色
        colors = [(255, 100, 100), (255, 255, 100), (255, 150, 100), (255, 50, 50)]
        color = colors[difficulty_index]
        draw_glowing_text(screen, difficulty_text, FONT_M, color, (color[0]//3, color[1]//3, color[2]//3),
                         (SCREEN_WIDTH - FONT_M.size(difficulty_text)[0]) // 2, 250)
        
        draw_text_center(screen, "← / → 切换，Enter返回", FONT_S, (180, 200, 220), 320)
        pygame.display.flip()
        clock.tick(60)

    elif state == STATE_LEADERBOARD:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    state = STATE_MENU
        
        draw_background(screen)
        draw_glowing_text(screen, "排行榜", FONT_L, (255, 255, 255), (255, 215, 0),
                         (SCREEN_WIDTH - FONT_L.size("排行榜")[0]) // 2, 60)
        
        if len(game_data.get("high_scores", [])) == 0:
            draw_text_center(screen, "暂无记录", FONT_M, (200, 210, 230), 200)
        else:
            for i, sc in enumerate(game_data["high_scores"][:10]):
                text = f"{i+1:02d}.  分数 {sc}"
                if i == 0:
                    color = (255, 215, 0)  # 金色
                    glow = (255, 215, 0, 100)
                elif i == 1:
                    color = (192, 192, 192)  # 银色
                    glow = (192, 192, 192, 80)
                elif i == 2:
                    color = (205, 127, 50)  # 铜色
                    glow = (205, 127, 50, 60)
                else:
                    color = (200, 210, 230)
                    glow = None
                
                y_pos = 150 + i * 35
                if glow:
                    draw_glowing_text(screen, text, FONT_M, color, glow[:3],
                                     (SCREEN_WIDTH - FONT_M.size(text)[0]) // 2, y_pos)
                else:
                    draw_text_center(screen, text, FONT_M, color, y_pos)
        
        draw_text_center(screen, "按 Enter 或 Esc 返回", FONT_S, (180, 200, 220), 520)
        pygame.display.flip()
        clock.tick(60)

    elif state == STATE_PLAY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
                elif event.key == pygame.K_ESCAPE:
                    state = STATE_MENU
        
        # 核心更新
        snake.move()
        snake.update()
        particle_system.update()
        
        if snake.check_collision():
            # 碰撞爆炸效果
            head = snake.body[0]
            for _ in range(30):
                particle_system.add_particle(
                    head[0] * GRID_SIZE + GRID_SIZE // 2,
                    head[1] * GRID_SIZE + GRID_SIZE // 2,
                    (255, 100, 100),
                    (random.uniform(-5, 5), random.uniform(-5, 5)),
                    60
                )
            
            if not saved_in_this_run:
                save_data(game_data, snake.score, snake.achievements)
                saved_in_this_run = True
            state = STATE_GAME_OVER
            
        if food and snake.body[0] == food.position:
            snake.eat_food(food.value)
            food = Food(snake.level)
            snake.check_achievements()
        if food is None:
            food = Food(snake.level)
        
        # 绘制
        draw_background(screen)
        snake.draw(screen)
        food.draw(screen)
        particle_system.draw(screen)
        
        # HUD with glow
        hud_text = f"分数: {snake.score}  等级: {snake.level}（{SNAKE_NAMES[snake.level]}） 难度: {DIFFICULTIES[difficulty_index]['name']}"
        draw_glowing_text(screen, hud_text, FONT_S, (255, 255, 255), (100, 150, 255), 12, 8)
        
        pygame.display.flip()
        clock.tick(current_speed)

    elif state == STATE_GAME_OVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = STATE_MENU
                elif event.key == pygame.K_r:
                    snake.reset()
                    food = Food(snake.level)
                    saved_in_this_run = False
                    state = STATE_PLAY
        
        particle_system.update()
        
        draw_background(screen)
        particle_system.draw(screen)
        
        draw_glowing_text(screen, "游戏结束", FONT_L, (255, 100, 100), (255, 0, 0),
                         (SCREEN_WIDTH - FONT_L.size("游戏结束")[0]) // 2, 120)
        
        score_text = f"得分：{snake.score}"
        draw_glowing_text(screen, score_text, FONT_M, (255, 215, 0), (255, 165, 0),
                         (SCREEN_WIDTH - FONT_M.size(score_text)[0]) // 2, 220)
        
        draw_text_center(screen, "Enter 返回菜单   R 重新开始", FONT_S, (200, 210, 230), 300)
        
        # 展示前3名
        draw_glowing_text(screen, "Top 3", FONT_M, (255, 255, 255), (100, 150, 255),
                         (SCREEN_WIDTH - FONT_M.size("Top 3")[0]) // 2, 380)
        
        top3 = game_data.get("high_scores", [])[:3]
        if not top3:
            draw_text_center(screen, "暂无记录", FONT_S, (200, 210, 230), 420)
        else:
            for i, sc in enumerate(top3):
                text = f"{i+1}. {sc}"
                colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
                color = colors[i] if i < 3 else (200, 210, 230)
                draw_text_center(screen, text, FONT_S, color, 420 + i * 28)
        
        pygame.display.flip()
        clock.tick(60)

# 退出游戏
pygame.quit()
sys.exit()
import math
import random
import sys
import pygame

# =========================================================
# INITIAL SETUP & CONFIGURATION
# =========================================================

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

WIDTH, HEIGHT = 900, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - Dynamic Speed & Auto-Level Edition")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (15, 15, 28)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (140, 150, 170)
COLOR_DARK_GRAY = (40, 45, 60)
COLOR_PADDLE = (230, 240, 255)
COLOR_BALL = (255, 255, 255)

ROW_COLORS = [
    (240, 70, 70),   # Red
    (255, 150, 50),  # Orange
    (255, 210, 60),  # Yellow
    (80, 200, 120),  # Green
    (80, 160, 255),  # Blue
    (170, 100, 230), # Purple
    (255, 110, 180)  # Pink
]

POWERUP_TYPES = {
    "WIDE":  {"color": (80, 220, 120), "symbol": "W", "duration": 8.0},
    "MULTI": {"color": (255, 200, 50),  "symbol": "M", "duration": 0.0},
    "SLOW":  {"color": (80, 180, 255), "symbol": "S", "duration": 5.0},
    "LIFE":  {"color": (255, 90, 140), "symbol": "+", "duration": 0.0}
}

font_title = pygame.font.SysFont("Verdana", 52, bold=True)
font_large = pygame.font.SysFont("Verdana", 36, bold=True)
font_ui = pygame.font.SysFont("Verdana", 18, bold=True)
font_small = pygame.font.SysFont("Verdana", 14, bold=True)

# =========================================================
# PROCEDURAL SOUND SYNTHESIS
# =========================================================

def create_synth_sound(freq_start, freq_end, duration_ms, wave_type="sine", volume=0.25):
    sample_rate = 44100
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = bytearray()
    
    for i in range(n_samples):
        t = i / sample_rate
        frac = i / n_samples
        freq = freq_start + (freq_end - freq_start) * frac
        
        if wave_type == "sine":
            val = math.sin(2 * math.pi * freq * t)
        elif wave_type == "square":
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave_type == "noise":
            val = random.uniform(-1.0, 1.0)
        else:
            val = 0
            
        decay = 1.0 - frac
        sample = int(val * decay * 32767 * volume)
        
        buf.extend(sample.to_bytes(2, byteorder="little", signed=True))
        buf.extend(sample.to_bytes(2, byteorder="little", signed=True))
        
    return pygame.mixer.Sound(bytes(buf))

try:
    snd_brick = create_synth_sound(450, 750, 50, "sine")
    snd_paddle = create_synth_sound(300, 180, 60, "sine")
    snd_wall = create_synth_sound(200, 120, 40, "sine")
    snd_powerup = create_synth_sound(400, 1000, 150, "sine")
    snd_life_lost = create_synth_sound(300, 80, 350, "square")
    snd_win = create_synth_sound(440, 880, 400, "sine")
except Exception:
    snd_brick = snd_paddle = snd_wall = snd_powerup = snd_life_lost = snd_win = None

def play_sound(sound):
    if sound:
        sound.play()

# =========================================================
# GAME CLASSES
# =========================================================

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.color = color
        self.size = random.randint(3, 6)
        self.life = random.randint(15, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.15)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


class ScorePopup:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 35
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            surf = font_small.render(self.text, True, self.color)
            surf.set_alpha(int((self.life / 35.0) * 255))
            surface.blit(surf, (self.x - surf.get_width() // 2, self.y))


class PowerUp:
    def __init__(self, x, y, p_type):
        self.rect = pygame.Rect(x - 14, y - 10, 28, 20)
        self.type = p_type
        self.speed = 2.8
        self.color = POWERUP_TYPES[p_type]["color"]
        self.symbol = POWERUP_TYPES[p_type]["symbol"]

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, width=2, border_radius=6)
        txt = font_small.render(self.symbol, True, (0, 0, 0))
        surface.blit(txt, txt.get_rect(center=self.rect.center))


class Ball:
    def __init__(self, x, y, base_speed=5.0):
        self.radius = 8
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.base_speed = base_speed
        self.speed_modifier = 1.0
        self.dx = 0.0
        self.dy = 0.0
        self.trail = []
        self.launch(base_speed)

    def launch(self, base_speed):
        self.base_speed = base_speed
        angle_deg = random.choice([
            random.uniform(-150, -120),
            random.uniform(-60, -30)
        ])
        rad = math.radians(angle_deg)
        spd = self.base_speed * self.speed_modifier
        self.dx = math.cos(rad) * spd
        self.dy = math.sin(rad) * spd

    def update(self, dynamic_speed_boost=0.0, speed_mult=1.0):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 6:
            self.trail.pop(0)

        current_speed = (self.base_speed + dynamic_speed_boost) * self.speed_modifier * speed_mult
        current_angle = math.atan2(self.dy, self.dx)
        self.dx = math.cos(current_angle) * current_speed
        self.dy = math.sin(current_angle) * current_speed

        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 120)
            size = max(2, int(self.radius * (i / len(self.trail))))
            t_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (255, 255, 255, alpha), (size, size), size)
            surface.blit(t_surf, (pos[0] - size, pos[1] - size))

        pygame.draw.circle(surface, COLOR_BALL, self.rect.center, self.radius)


class Game:
    def __init__(self):
        self.state = "MAIN_MENU"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.max_levels = 5
        self.combo = 0
        
        self.level_time = 0.0
        self.time_limit_per_level = 45.0
        self.dynamic_speed_boost = 0.0
        
        self.timer_wide = 0.0
        self.timer_slow = 0.0

        self.paddle = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 50, 140, 18)
        self.base_paddle_width = 140
        self.paddle_speed = 9
        
        self.balls = []
        self.bricks = []
        self.particles = []
        self.popups = []
        self.powerups = []

    def get_level_settings(self):
        base_speed = 5.0 + (self.level - 1) * 0.8
        paddle_w = max(90, 140 - (self.level - 1) * 10)
        rows = min(8, 4 + self.level)
        return base_speed, paddle_w, rows

    def reset_ball_and_paddle(self):
        base_speed, paddle_w, _ = self.get_level_settings()
        self.base_paddle_width = paddle_w
        self.paddle.width = paddle_w * (1.5 if self.timer_wide > 0 else 1.0)
        self.paddle.centerx = WIDTH // 2
        self.paddle.bottom = HEIGHT - 40

        self.balls.clear()
        ball = Ball(WIDTH // 2, HEIGHT // 2, base_speed)
        self.balls.append(ball)

    def full_reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0
        self.level_time = 0.0
        self.dynamic_speed_boost = 0.0
        self.timer_wide = 0.0
        self.timer_slow = 0.0
        self.powerups.clear()
        self.particles.clear()
        self.popups.clear()
        self.setup_level()

    def setup_level(self):
        self.level_time = 0.0
        self.dynamic_speed_boost = 0.0
        self.reset_ball_and_paddle()
        self.create_bricks()

    def create_bricks(self):
        self.bricks.clear()
        _, _, rows = self.get_level_settings()
        cols = 10
        b_width, b_height = 76, 22
        gap = 8
        start_x = (WIDTH - (cols * b_width + (cols - 1) * gap)) // 2
        start_y = 80

        layouts = ["FULL", "CHECKERBOARD", "PYRAMID", "GAPS"]
        chosen_layout = random.choice(layouts)

        for r in range(rows):
            for c in range(cols):
                spawn = True
                
                if chosen_layout == "CHECKERBOARD":
                    if (r + c) % 2 != 0:
                        spawn = False
                elif chosen_layout == "PYRAMID":
                    center = cols // 2
                    dist = abs(c - center)
                    if dist > (r + 1):
                        spawn = False
                elif chosen_layout == "GAPS":
                    if c in [2, 7] or r in [1, 4]:
                        spawn = False

                if spawn:
                    bx = start_x + c * (b_width + gap)
                    by = start_y + r * (b_height + gap)
                    rect = pygame.Rect(bx, by, b_width, b_height)
                    
                    color = ROW_COLORS[r % len(ROW_COLORS)]
                    b_type = "NORMAL"
                    hp = 1
                    pts = 10

                    if self.level >= 2 and r == 0 and random.random() < 0.5:
                        b_type = "STRONG"
                        hp = 2
                        pts = 20
                        color = (200, 200, 210)
                    elif self.level >= 3 and random.random() < 0.12:
                        b_type = "SPECIAL"
                        hp = 1
                        pts = 30
                        color = (255, 215, 0)

                    self.bricks.append({
                        "rect": rect,
                        "color": color,
                        "hp": hp,
                        "max_hp": hp,
                        "points": pts,
                        "type": b_type
                    })

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def handle_brick_destruction(self, brick):
        self.combo += 1
        combo_bonus = (self.combo - 1) * 10
        total_pts = brick["points"] + combo_bonus
        self.score += total_pts

        play_sound(snd_brick)
        self.spawn_particles(brick["rect"].centerx, brick["rect"].centery, brick["color"])

        popup_str = f"+{total_pts}" if self.combo <= 1 else f"+{total_pts} ({self.combo}x)"
        self.popups.append(ScorePopup(brick["rect"].centerx, brick["rect"].centery, popup_str, brick["color"]))

        drop_chance = 0.25 if brick["type"] == "SPECIAL" else 0.08
        if random.random() < drop_chance:
            p_type = random.choice(list(POWERUP_TYPES.keys()))
            self.powerups.append(PowerUp(brick["rect"].centerx, brick["rect"].centery, p_type))

    def apply_powerup(self, p_type):
        play_sound(snd_powerup)
        if p_type == "WIDE":
            self.timer_wide = POWERUP_TYPES["WIDE"]["duration"]
            self.paddle.width = int(self.base_paddle_width * 1.5)
        elif p_type == "SLOW":
            self.timer_slow = POWERUP_TYPES["SLOW"]["duration"]
        elif p_type == "MULTI":
            if self.balls:
                b = self.balls[0]
                new_b = Ball(b.rect.centerx, b.rect.centery, b.base_speed)
                new_b.dx = -b.dx
                new_b.dy = b.dy
                self.balls.append(new_b)
        elif p_type == "LIFE":
            self.lives += 1
            self.popups.append(ScorePopup(self.paddle.centerx, self.paddle.top - 10, "+1 LIFE!", (255, 100, 150)))

    def advance_level(self):
        if self.level >= self.max_levels:
            self.state = "WIN"
            play_sound(snd_win)
        else:
            self.state = "LEVEL_COMPLETE"
            play_sound(snd_win)

    def update(self, dt):
        if self.state != "PLAYING":
            return

        self.level_time += dt
        self.dynamic_speed_boost = self.level_time * 0.1

        if self.level_time >= self.time_limit_per_level:
            self.advance_level()
            return

        if self.timer_wide > 0:
            self.timer_wide -= dt
            if self.timer_wide <= 0:
                self.paddle.width = self.base_paddle_width

        if self.timer_slow > 0:
            self.timer_slow -= dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.x -= self.paddle_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.x += self.paddle_speed

        self.paddle.left = max(0, self.paddle.left)
        self.paddle.right = min(WIDTH, self.paddle.right)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        for pop in self.popups[:]:
            pop.update()
            if pop.life <= 0:
                self.popups.remove(pop)

        for pu in self.powerups[:]:
            pu.update()
            if pu.rect.colliderect(self.paddle):
                self.apply_powerup(pu.type)
                self.powerups.remove(pu)
            elif pu.rect.top > HEIGHT:
                self.powerups.remove(pu)

        speed_mult = 0.65 if self.timer_slow > 0 else 1.0

        for ball in self.balls[:]:
            ball.update(self.dynamic_speed_boost, speed_mult)

            if ball.rect.left <= 0:
                ball.rect.left = 0
                ball.dx = abs(ball.dx)
                play_sound(snd_wall)
            elif ball.rect.right >= WIDTH:
                ball.rect.right = WIDTH
                ball.dx = -abs(ball.dx)
                play_sound(snd_wall)

            if ball.rect.top <= 0:
                ball.rect.top = 0
                ball.dy = abs(ball.dy)
                play_sound(snd_wall)

            if ball.rect.colliderect(self.paddle) and ball.dy > 0:
                ball.rect.bottom = self.paddle.top
                play_sound(snd_paddle)

                offset = (ball.rect.centerx - self.paddle.centerx) / (self.paddle.width / 2)
                offset = max(-0.9, min(0.9, offset))
                
                speed = math.hypot(ball.dx, ball.dy)
                angle = offset * (math.pi / 3)
                ball.dx = speed * math.sin(angle)
                ball.dy = -speed * math.cos(angle)

            for brick in self.bricks[:]:
                if ball.rect.colliderect(brick["rect"]):
                    overlap_left = ball.rect.right - brick["rect"].left
                    overlap_right = brick["rect"].right - ball.rect.left
                    overlap_top = ball.rect.bottom - brick["rect"].top
                    overlap_bottom = brick["rect"].bottom - ball.rect.top

                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                    if min_overlap == overlap_left or min_overlap == overlap_right:
                        ball.dx = -ball.dx
                    else:
                        ball.dy = -ball.dy

                    brick["hp"] -= 1
                    if brick["hp"] <= 0:
                        self.handle_brick_destruction(brick)
                        self.bricks.remove(brick)
                    else:
                        play_sound(snd_brick)
                        brick["color"] = (160, 160, 175)
                    break

            if ball.rect.top > HEIGHT:
                self.balls.remove(ball)

        if len(self.balls) == 0:
            self.lives -= 1
            self.combo = 0
            play_sound(snd_life_lost)
            if self.lives <= 0:
                self.state = "GAME_OVER"
            else:
                self.reset_ball_and_paddle()

        if len(self.bricks) == 0:
            self.advance_level()

    # =========================================================
    # RENDER METHODS
    # =========================================================

    def draw_hud(self, surface):
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (0, 0, WIDTH, 45))
        pygame.draw.line(surface, COLOR_GRAY, (0, 45), (WIDTH, 45), 2)

        time_left = max(0, int(self.time_limit_per_level - self.level_time))
        txt_score = font_ui.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        txt_level = font_ui.render(f"LEVEL: {self.level}/{self.max_levels}", True, (255, 215, 0))
        txt_timer = font_ui.render(f"NEXT LVL: {time_left}s", True, (80, 200, 255))
        
        # Fixed font character mapping for Lives indicator
        txt_lives = font_ui.render(f"LIVES: {self.lives}", True, (255, 90, 120))

        surface.blit(txt_score, (20, 12))
        surface.blit(txt_level, (220, 12))
        surface.blit(txt_timer, (450, 12))
        surface.blit(txt_lives, (WIDTH - txt_lives.get_width() - 20, 12))

        if self.combo > 1:
            c_surf = font_small.render(f"COMBO {self.combo}x!", True, (255, 200, 50))
            surface.blit(c_surf, (20, 50))

    def draw_game(self, surface):
        surface.fill(COLOR_BG)

        for b in self.bricks:
            r = b["rect"]
            pygame.draw.rect(surface, b["color"], r, border_radius=4)
            pygame.draw.rect(surface, (255, 255, 255, 50), r, width=1, border_radius=4)

        for pu in self.powerups:
            pu.draw(surface)

        for p in self.particles:
            p.draw(surface)

        pygame.draw.rect(surface, COLOR_PADDLE, self.paddle, border_radius=6)
        for ball in self.balls:
            ball.draw(surface)

        for pop in self.popups:
            pop.draw(surface)

        self.draw_hud(surface)

    def draw_menu(self, surface):
        surface.fill(COLOR_BG)
        
        t = font_title.render("BREAKOUT", True, COLOR_WHITE)
        sub = font_ui.render("DYNAMIC SPEED & AUTO-LEVELS", True, (255, 200, 50))
        
        start_lbl = font_large.render("Press SPACE / ENTER to Start", True, (80, 220, 120))
        quit_lbl = font_ui.render("Press ESC to Quit", True, COLOR_GRAY)

        surface.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 65)))
        surface.blit(start_lbl, start_lbl.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
        surface.blit(quit_lbl, quit_lbl.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))

        ctrl_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 160, 400, 80)
        pygame.draw.rect(surface, COLOR_DARK_GRAY, ctrl_box, border_radius=8)
        c1 = font_small.render("Controls: A/D or LEFT/RIGHT Arrow Keys", True, COLOR_WHITE)
        c2 = font_small.render("Pause Game: P Key", True, COLOR_GRAY)
        surface.blit(c1, c1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 185)))
        surface.blit(c2, c2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 215)))

    def draw_overlay(self, surface, title_text, sub_text, title_color=COLOR_WHITE):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 210))
        surface.blit(overlay, (0, 0))

        t = font_title.render(title_text, True, title_color)
        s = font_ui.render(sub_text, True, COLOR_WHITE)

        surface.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        surface.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

# =========================================================
# MAIN EXECUTION LOOP
# =========================================================

def main():
    game = Game()

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if game.state == "MAIN_MENU":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        game.full_reset()
                        game.state = "PLAYING"

                elif game.state == "PLAYING":
                    if event.key == pygame.K_p:
                        game.state = "PAUSED"

                elif game.state == "PAUSED":
                    if event.key == pygame.K_p:
                        game.state = "PLAYING"

                elif game.state == "LEVEL_COMPLETE":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        game.level += 1
                        game.setup_level()
                        game.state = "PLAYING"

                elif game.state in ["GAME_OVER", "WIN"]:
                    if event.key == pygame.K_r:
                        game.full_reset()
                        game.state = "PLAYING"

        if game.state == "MAIN_MENU":
            game.draw_menu(screen)

        elif game.state == "PLAYING":
            game.update(dt)
            game.draw_game(screen)

        elif game.state == "PAUSED":
            game.draw_game(screen)
            game.draw_overlay(screen, "PAUSED", "Press P to Resume")

        elif game.state == "LEVEL_COMPLETE":
            game.draw_game(screen)
            game.draw_overlay(screen, f"LEVEL {game.level} COMPLETE!", "Press SPACE / ENTER for Next Level", (80, 220, 120))

        elif game.state == "GAME_OVER":
            game.draw_game(screen)
            game.draw_overlay(screen, "GAME OVER", f"FINAL SCORE: {game.score}  |  Press R to Restart or ESC for Menu", (255, 80, 80))

        elif game.state == "WIN":
            game.draw_game(screen)
            game.draw_overlay(screen, "YOU WIN!", f"VICTORY SCORE: {game.score}  |  Press R to Play Again or ESC for Menu", (255, 215, 0))

        pygame.display.flip()


if __name__ == "__main__":
    main()
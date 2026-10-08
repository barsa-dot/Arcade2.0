"""
Space Shooter - Classic 2D Arcade Game
Developed for the Arcade 2.0 Hackathon Project

Controls:
- A / Left Arrow  : Move Left
- D / Right Arrow : Move Right
- SPACE           : Shoot (and Start Game from title screen)
- P               : Pause / Resume
- R               : Restart (after Game Over)
- ESC             : Exit
"""

import os
import sys
import random
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Palette - Dark arcade space aesthetic
COLOR_SPACE_BG       = (11, 14, 25)
COLOR_STAR_DIM       = (120, 140, 180)
COLOR_STAR_BRIGHT    = (230, 240, 255)
COLOR_PLAYER         = (0, 220, 255)       # Neon Cyan
COLOR_PLAYER_WING    = (0, 150, 200)
COLOR_PLAYER_COCKPIT = (220, 250, 255)
COLOR_PLAYER_FLAME   = (255, 140, 20)      # Thruster orange
COLOR_ENEMY          = (255, 65, 80)       # Crimson Alien
COLOR_ENEMY_WING     = (200, 35, 50)
COLOR_ENEMY_EYE      = (255, 220, 60)      # Yellow core
COLOR_BULLET         = (255, 235, 75)      # Laser Yellow
COLOR_BULLET_GLOW    = (255, 170, 0)
COLOR_WHITE          = (240, 245, 255)
COLOR_GRAY           = (150, 165, 185)
COLOR_DARK_OVERLAY   = (5, 8, 16, 200)
COLOR_GOLD           = (255, 215, 0)
COLOR_RED            = (255, 70, 70)

# High score file path (kept inside the game folder)
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(GAME_DIR, "highscore.txt")


# ==============================================================================
# HIGH SCORE UTILITIES
# ==============================================================================
def load_high_score() -> int:
    """Read local high score from text file. Returns 0 if not found or corrupted."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as file:
                content = file.read().strip()
                return int(content) if content.isdigit() else 0
        except Exception:
            return 0
    return 0


def save_high_score(score: int) -> None:
    """Save high score to text file."""
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(int(score)))
    except Exception:
        pass


# ==============================================================================
# GAME ENTITIES
# ==============================================================================
class Star:
    """Background star creating an arcade scrolling space effect."""
    def __init__(self, random_y: bool = True):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT) if random_y else random.randint(-20, 0)
        self.speed = random.uniform(0.6, 2.4)
        self.size = 1 if self.speed < 1.5 else 2
        self.color = COLOR_STAR_BRIGHT if self.speed > 1.6 else COLOR_STAR_DIM

    def update(self) -> None:
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class Bullet:
    """Player laser bullet."""
    def __init__(self, x: float, y: float):
        self.width = 4
        self.height = 14
        self.speed = 10
        self.rect = pygame.Rect(x - self.width // 2, y - self.height, self.width, self.height)

    def update(self) -> None:
        self.rect.y -= self.speed

    def draw(self, surface: pygame.Surface) -> None:
        # Outer laser glow
        glow_rect = pygame.Rect(self.rect.x - 1, self.rect.y - 1, self.width + 2, self.height + 2)
        pygame.draw.rect(surface, COLOR_BULLET_GLOW, glow_rect, border_radius=2)
        # Inner bright core
        pygame.draw.rect(surface, COLOR_BULLET, self.rect, border_radius=2)


class Player:
    """Player spaceship entity."""
    def __init__(self):
        self.width = 44
        self.height = 46
        self.speed = 6.0
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincible_timer = 0  # Flash after taking hit
        self.shoot_cooldown_ms = 220
        self.last_shot_time = -self.shoot_cooldown_ms
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.reset_position()

    def reset_position(self) -> None:
        self.rect.x = (SCREEN_WIDTH - self.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.height - 25

    def reset_all(self) -> None:
        self.lives = self.max_lives
        self.invincible_timer = 0
        self.last_shot_time = -self.shoot_cooldown_ms
        self.reset_position()

    def move_left(self) -> None:
        self.rect.x -= self.speed
        if self.rect.x < 10:
            self.rect.x = 10

    def move_right(self) -> None:
        self.rect.x += self.speed
        if self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10

    def try_shoot(self, current_time: int) -> Bullet | None:
        if current_time - self.last_shot_time >= self.shoot_cooldown_ms:
            self.last_shot_time = current_time
            # Spawn bullet from top center of ship
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def update(self) -> None:
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def draw(self, surface: pygame.Surface, frame_count: int) -> None:
        # Blink when invulnerability timer is active
        if self.invincible_timer > 0 and (frame_count // 4) % 2 == 0:
            return

        x, y = self.rect.x, self.rect.y
        w, h = self.width, self.height

        # 1. Animated Thruster Flame
        flame_flicker = (frame_count % 3) * 3
        flame_poly = [
            (x + w * 0.38, y + h - 4),
            (x + w * 0.62, y + h - 4),
            (x + w * 0.50, y + h + 8 + flame_flicker)
        ]
        pygame.draw.polygon(surface, COLOR_PLAYER_FLAME, flame_poly)

        # 2. Outer Wings
        left_wing = [
            (x, y + h - 2),
            (x + w * 0.35, y + h * 0.55),
            (x + w * 0.35, y + h - 4)
        ]
        right_wing = [
            (x + w, y + h - 2),
            (x + w * 0.65, y + h * 0.55),
            (x + w * 0.65, y + h - 4)
        ]
        pygame.draw.polygon(surface, COLOR_PLAYER_WING, left_wing)
        pygame.draw.polygon(surface, COLOR_PLAYER_WING, right_wing)

        # 3. Main Ship Fuselage (Sleek aerodynamic triangle)
        body_poly = [
            (x + w * 0.50, y),             # Nose tip
            (x + w * 0.88, y + h - 4),     # Bottom right
            (x + w * 0.50, y + h - 10),    # Center bottom recess
            (x + w * 0.12, y + h - 4)      # Bottom left
        ]
        pygame.draw.polygon(surface, COLOR_PLAYER, body_poly)

        # 4. Cockpit Windshield (Glowing cyan glass)
        cockpit_rect = pygame.Rect(x + w * 0.42, y + h * 0.30, w * 0.16, h * 0.28)
        pygame.draw.ellipse(surface, COLOR_PLAYER_COCKPIT, cockpit_rect)


class Enemy:
    """Alien enemy ship descending toward the player."""
    def __init__(self, speed: float):
        self.width = 38
        self.height = 32
        self.speed = speed
        self.rect = pygame.Rect(
            random.randint(20, SCREEN_WIDTH - self.width - 20),
            -self.height,
            self.width,
            self.height
        )

    def update(self) -> None:
        self.rect.y += self.speed

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.rect.x, self.rect.y
        w, h = self.width, self.height

        # Side wing accents
        left_wing = [(x, y + 8), (x + w * 0.25, y + h), (x + w * 0.25, y)]
        right_wing = [(x + w, y + 8), (x + w * 0.75, y + h), (x + w * 0.75, y)]
        pygame.draw.polygon(surface, COLOR_ENEMY_WING, left_wing)
        pygame.draw.polygon(surface, COLOR_ENEMY_WING, right_wing)

        # Main aggressive inverted delta body
        body_poly = [
            (x + w * 0.50, y + h),         # Bottom stinger point
            (x + w * 0.15, y + 4),         # Top left
            (x + w * 0.50, y + 10),        # Top center dip
            (x + w * 0.85, y + 4)          # Top right
        ]
        pygame.draw.polygon(surface, COLOR_ENEMY, body_poly)

        # Central alien eye / core
        eye_rect = pygame.Rect(x + w * 0.40, y + h * 0.35, w * 0.20, h * 0.25)
        pygame.draw.ellipse(surface, COLOR_ENEMY_EYE, eye_rect)


class Particle:
    """Spark particle produced on enemy explosions."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3.0, 3.0)
        self.vy = random.uniform(-3.0, 3.0)
        self.life = random.randint(12, 22)
        self.color = random.choice([COLOR_BULLET, COLOR_PLAYER_FLAME, COLOR_ENEMY])

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface: pygame.Surface) -> None:
        if self.life > 0:
            size = 2 if self.life > 8 else 1
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


# ==============================================================================
# MAIN GAME CLASS
# ==============================================================================
class SpaceShooterGame:
    """Coordinates state, entities, logic, and rendering."""
    # State identifiers
    STATE_START     = "START"
    STATE_PLAYING   = "PLAYING"
    STATE_PAUSED    = "PAUSED"
    STATE_GAME_OVER = "GAME_OVER"

    def __init__(self):
        pygame.init()
        # Initialize mixer gracefully (if no sound hardware, won't crash)
        try:
            pygame.mixer.init()
        except Exception:
            pass

        pygame.display.set_caption("Space Shooter - Arcade 2.0")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("consolas", 46, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_ui = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 16)

        # Starfield
        self.stars = [Star() for _ in range(65)]

        # Gameplay Entities
        self.player = Player()
        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.particles: list[Particle] = []

        # Game State & Progression
        self.state = self.STATE_START
        self.score = 0
        self.high_score = load_high_score()
        self.frame_count = 0
        self.spawn_timer = 0
        self.is_new_high_score = False

    def restart_game(self) -> None:
        """Reset all game variables to start fresh."""
        self.score = 0
        self.player.reset_all()
        self.bullets.clear()
        self.enemies.clear()
        self.particles.clear()
        self.spawn_timer = 0
        self.is_new_high_score = False
        self.state = self.STATE_PLAYING

    def get_current_enemy_speed(self) -> float:
        """Calculate dynamic enemy speed based on score."""
        # Starts at 2.0 px/frame, increases smoothly up to 6.5 px/frame
        return 2.0 + min(self.score * 0.12, 4.5)

    def get_spawn_interval(self) -> int:
        """Calculate dynamic spawn interval in frames."""
        # 60 frames = 1 second. Drops to a minimum of 28 frames as score rises.
        return max(28, 62 - int(self.score * 0.8))

    def trigger_explosion(self, x: float, y: float, count: int = 10) -> None:
        """Create sparkling particle burst at position."""
        for _ in range(count):
            self.particles.append(Particle(x, y))

    def handle_events(self) -> bool:
        """Process input events. Returns False when application should close."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # Universal ESC to exit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # State: START SCREEN
                if self.state == self.STATE_START:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()

                # State: PLAYING
                elif self.state == self.STATE_PLAYING:
                    if event.key == pygame.K_p:
                        self.state = self.STATE_PAUSED
                    elif event.key == pygame.K_SPACE:
                        now = pygame.time.get_ticks()
                        new_bullet = self.player.try_shoot(now)
                        if new_bullet:
                            self.bullets.append(new_bullet)

                # State: PAUSED
                elif self.state == self.STATE_PAUSED:
                    if event.key == pygame.K_p:
                        self.state = self.STATE_PLAYING

                # State: GAME OVER
                elif self.state == self.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.restart_game()

        return True

    def update(self) -> None:
        """Update game logic per frame."""
        self.frame_count += 1

        # Background stars always move
        for star in self.stars:
            star.update()

        # Floating explosion particles always update
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Only execute gameplay mechanics when actively PLAYING
        if self.state != self.STATE_PLAYING:
            return

        # 1. Continuous Player Input (Left / Right & Space hold)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            new_bullet = self.player.try_shoot(now)
            if new_bullet:
                self.bullets.append(new_bullet)

        self.player.update()

        # 2. Update Bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)

        # 3. Spawn Enemies
        self.spawn_timer += 1
        if self.spawn_timer >= self.get_spawn_interval():
            self.spawn_timer = 0
            speed = self.get_current_enemy_speed()
            self.enemies.append(Enemy(speed))

        # 4. Update Enemies & Check Player Defense Area
        for enemy in self.enemies[:]:
            enemy.update()

            # Enemy reaches player defense area or collides directly with player
            defense_breached = enemy.rect.bottom >= SCREEN_HEIGHT - 35
            player_hit = enemy.rect.colliderect(self.player.rect)

            if defense_breached or player_hit:
                self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, 14)
                self.enemies.remove(enemy)
                self.player.lives -= 1
                self.player.invincible_timer = 30  # Flash for half a second

                # Check for Game Over condition
                if self.player.lives <= 0:
                    self.state = self.STATE_GAME_OVER
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.is_new_high_score = True
                        save_high_score(self.high_score)
                    break

        # 5. Bullet vs Enemy Collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    # Collision detected!
                    self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, 12)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

                    self.score += 1

                    # Live high score tracking
                    if self.score > self.high_score:
                        self.high_score = self.score
                    break

    def draw_hud(self) -> None:
        """Render in-game HUD: Score, High Score, and Lives."""
        # Top-left Score
        score_text = self.font_ui.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (25, 20))

        # Top-center High Score
        high_text = self.font_ui.render(f"HIGH: {self.high_score}", True, COLOR_GOLD)
        self.screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 20))

        # Top-right Lives
        lives_label = self.font_ui.render("LIVES:", True, COLOR_WHITE)
        self.screen.blit(lives_label, (SCREEN_WIDTH - 180, 20))

        # Draw mini spaceship icons for remaining lives
        icon_start_x = SCREEN_WIDTH - 105
        for i in range(self.player.lives):
            ix = icon_start_x + i * 26
            iy = 22
            # Small ship icon polygon
            mini_ship = [(ix + 8, iy), (ix + 16, iy + 16), (ix + 8, iy + 13), (ix, iy + 16)]
            pygame.draw.polygon(self.screen, COLOR_PLAYER, mini_ship)

    def draw_start_screen(self) -> None:
        """Render arcade title splash screen."""
        # Semi-transparent dark overlay for clean presentation
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 22, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_surf = self.font_title.render("SPACE SHOOTER", True, COLOR_PLAYER)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 130))

        # Subtitle
        sub_surf = self.font_small.render("ARCADE 2.0  •  COLLEGE HACKATHON EDITION", True, COLOR_GRAY)
        self.screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 190))

        # Instructions Box
        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 235, 360, 180)
        pygame.draw.rect(self.screen, (18, 24, 42), box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (40, 60, 100), box_rect, width=2, border_radius=8)

        controls = [
            ("Move Left",  "A / Left Arrow"),
            ("Move Right", "D / Right Arrow"),
            ("Shoot",      "SPACE"),
            ("Pause",      "P"),
            ("Exit",       "ESC"),
        ]
        for idx, (action, key_desc) in enumerate(controls):
            act_s = self.font_small.render(action, True, COLOR_WHITE)
            key_s = self.font_small.render(key_desc, True, COLOR_PLAYER)
            row_y = 250 + idx * 30
            self.screen.blit(act_s, (box_rect.x + 25, row_y))
            self.screen.blit(key_s, (box_rect.right - 25 - key_s.get_width(), row_y))

        # High score banner
        record_surf = self.font_ui.render(f"CURRENT RECORD: {self.high_score}", True, COLOR_GOLD)
        self.screen.blit(record_surf, (SCREEN_WIDTH // 2 - record_surf.get_width() // 2, 440))

        # Flashing "Press SPACE to Start"
        if (self.frame_count // 30) % 2 == 0:
            prompt_surf = self.font_medium.render("PRESS [SPACE] TO START", True, COLOR_WHITE)
            self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 495))

    def draw_pause_screen(self) -> None:
        """Render pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 16, 190))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("GAME PAUSED", True, COLOR_PLAYER)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 230))

        prompt = self.font_medium.render("Press P to Resume", True, COLOR_WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 310))

    def draw_game_over_screen(self) -> None:
        """Render Game Over summary screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 5, 8, 215))
        self.screen.blit(overlay, (0, 0))

        # Game Over Banner
        go_surf = self.font_title.render("GAME OVER", True, COLOR_RED)
        self.screen.blit(go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, 150))

        # Score Breakdown Card
        card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 225, 320, 135)
        pygame.draw.rect(self.screen, (22, 16, 24), card_rect, border_radius=8)
        pygame.draw.rect(self.screen, (80, 30, 40), card_rect, width=2, border_radius=8)

        final_s = self.font_medium.render(f"Final Score:  {self.score}", True, COLOR_WHITE)
        self.screen.blit(final_s, (SCREEN_WIDTH // 2 - final_s.get_width() // 2, 250))

        high_s = self.font_medium.render(f"High Score:   {self.high_score}", True, COLOR_GOLD)
        self.screen.blit(high_s, (SCREEN_WIDTH // 2 - high_s.get_width() // 2, 290))

        if self.is_new_high_score and self.score > 0:
            new_best = self.font_small.render("★ NEW PERSONAL BEST! ★", True, COLOR_GOLD)
            self.screen.blit(new_best, (SCREEN_WIDTH // 2 - new_best.get_width() // 2, 330))

        # Flashing Restart Prompt
        if (self.frame_count // 25) % 2 == 0:
            restart_s = self.font_medium.render("PRESS [R] TO RESTART", True, COLOR_PLAYER)
            self.screen.blit(restart_s, (SCREEN_WIDTH // 2 - restart_s.get_width() // 2, 400))

        exit_s = self.font_small.render("Press [ESC] to Exit", True, COLOR_GRAY)
        self.screen.blit(exit_s, (SCREEN_WIDTH // 2 - exit_s.get_width() // 2, 455))

    def render(self) -> None:
        """Render complete frame."""
        # 1. Dark space backdrop
        self.screen.fill(COLOR_SPACE_BG)

        # 2. Stars
        for star in self.stars:
            star.draw(self.screen)

        # 3. Bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # 4. Enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # 5. Explosions
        for particle in self.particles:
            particle.draw(self.screen)

        # 6. Player
        if self.state in (self.STATE_PLAYING, self.STATE_PAUSED):
            self.player.draw(self.screen, self.frame_count)

        # 7. UI / Overlays depending on state
        if self.state == self.STATE_PLAYING:
            self.draw_hud()
        elif self.state == self.STATE_START:
            self.draw_start_screen()
        elif self.state == self.STATE_PAUSED:
            self.draw_hud()
            self.draw_pause_screen()
        elif self.state == self.STATE_GAME_OVER:
            self.draw_hud()
            self.draw_game_over_screen()

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ==============================================================================
# ENTRY POINT
# ==============================================================================
def main():
    game = SpaceShooterGame()
    game.run()


if __name__ == "__main__":
    main()

import pygame
import sys
import os
import subprocess
import math


# ============================================================
# INITIAL SETUP
# ============================================================

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade 2.0")

clock = pygame.time.Clock()


# ============================================================
# PATHS
# ============================================================

# Project root = F:\projects\Arcade2.0
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


GAMES = {
    1: {
        "name": "BREAKOUT",
        "game_file": os.path.join(BASE_DIR, "breakout", "main.py"),
        "score_file": os.path.join(BASE_DIR, "breakout", "highscore.txt"),
    },

    2: {
        "name": "PONG",
        "game_file": os.path.join(BASE_DIR, "pong", "main.py"),
        "score_file": os.path.join(BASE_DIR, "pong", "highscore.txt"),
    },

    3: {
        "name": "SPACE SHOOTER",
        "game_file": os.path.join(BASE_DIR, "space_shooter", "main.py"),
        "score_file": os.path.join(BASE_DIR, "space_shooter", "highscore.txt"),
    },

    4: {
        "name": "SNAKE",
        "game_file": os.path.join(BASE_DIR, "snake", "main.py"),
        "score_file": os.path.join(BASE_DIR, "snake", "highscore.txt"),
    },
}


# ============================================================
# FONTS
# ============================================================

TITLE_FONT = pygame.font.SysFont("arial", 76, bold=True)
SUBTITLE_FONT = pygame.font.SysFont("arial", 30, bold=True)
GAME_FONT = pygame.font.SysFont("arial", 27, bold=True)
SCORE_FONT = pygame.font.SysFont("consolas", 31, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 19)


# ============================================================
# COLORS
# ============================================================

BACKGROUND = (12, 12, 25)
WHITE = (245, 245, 245)
GRAY = (143, 160, 183)
YELLOW = (255, 215, 70)
GREEN = (80, 220, 130)
BLUE = (80, 160, 255)
RED = (240, 90, 90)
PURPLE = (180, 100, 255)
DARK_PANEL = (20, 27, 48)
GAME_COLORS = {
    1: (255, 174, 74),
    2: (53, 216, 255),
    3: (223, 105, 255),
    4: (105, 230, 139),
}


# ============================================================
# HIGH SCORE SYSTEM
# ============================================================

def read_highscore(score_file):
    """
    Read a game's high score.

    If the file doesn't exist or contains invalid data,
    return 0 instead of crashing the Hub.
    """

    try:
        if not os.path.exists(score_file):
            return 0

        with open(score_file, "r", encoding="utf-8") as file:
            value = file.read().strip()

        if value == "":
            return 0

        return int(value)

    except (ValueError, OSError):
        return 0


def get_all_scores():
    """
    Read the latest high score from every game.
    """

    scores = {}

    for number, game in GAMES.items():
        scores[number] = read_highscore(game["score_file"])

    return scores


# ============================================================
# GAME LAUNCHER
# ============================================================

def launch_game(game_number):
    """
    Launch the selected game as a separate Python process.

    When the game closes, execution returns here and
    the Arcade Hub starts again.
    """

    game = GAMES[game_number]

    game_file = game["game_file"]

    if not os.path.exists(game_file):

        print()
        print("========================================")
        print("GAME NOT FOUND")
        print("========================================")
        print(game_file)
        print("========================================")
        print()

        return

    # Hide the Hub window while the game is running.
    pygame.quit()

    try:

        subprocess.run(
            [sys.executable, game_file],
            cwd=os.path.dirname(game_file)
        )

    except Exception as error:

        print()
        print("Error while launching game:")
        print(error)
        print()

    # Re-initialize Pygame after the game closes.
    pygame.init()

    global screen

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Arcade 2.0"
    )


# ============================================================
# DRAW TEXT
# ============================================================

def draw_centered_text(
    text,
    font,
    color,
    y
):

    rendered = font.render(
        text,
        True,
        color
    )

    x = WIDTH // 2 - rendered.get_width() // 2

    screen.blit(
        rendered,
        (x, y)
    )


# ============================================================
# DRAW GAME ROW
# ============================================================

def draw_game_row(
    number,
    name,
    score,
    y,
    selected
):

    accent = GAME_COLORS[number]

    if selected:
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 500)
        border_color = tuple(
            min(255, int(channel * (0.82 + 0.18 * pulse)))
            for channel in accent
        )
        pygame.draw.rect(
            screen,
            (32, 41, 67),
            (83, y - 5, 834, 48),
            border_radius=12,
        )
        pygame.draw.rect(
            screen,
            border_color,
            (83, y - 5, 834, 48),
            width=2,
            border_radius=12,
        )

    number_text = GAME_FONT.render(
        f"{number}.",
        True,
        accent
    )

    name_text = GAME_FONT.render(
        name,
        True,
        WHITE if selected else (208, 220, 235)
    )

    score_text = SCORE_FONT.render(
        str(score),
        True,
        accent
    )

    pygame.draw.rect(
        screen,
        accent,
        (103, y + 3, 5, 28),
        border_radius=3,
    )

    screen.blit(
        number_text,
        (130, y)
    )

    screen.blit(
        name_text,
        (190, y + 2)
    )

    screen.blit(
        score_text,
        (835 - score_text.get_width(), y)
    )


# ============================================================
# MAIN HUB
# ============================================================

def main():

    running = True

    selected_game = 1

    while running:

        # ----------------------------------------------------
        # Refresh scores every frame.
        # This means the Hall of Fame updates after games.
        # ----------------------------------------------------

        scores = get_all_scores()

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                # Quit Hub
                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_q
                ):

                    running = False

                # Select game
                elif event.key == pygame.K_1:

                    selected_game = 1

                elif event.key == pygame.K_2:

                    selected_game = 2

                elif event.key == pygame.K_3:

                    selected_game = 3

                elif event.key == pygame.K_4:

                    selected_game = 4

                # Move selection
                elif event.key == pygame.K_UP:

                    selected_game -= 1

                    if selected_game < 1:
                        selected_game = 4

                elif event.key == pygame.K_DOWN:

                    selected_game += 1

                    if selected_game > 4:
                        selected_game = 1

                # Launch selected game
                elif event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER
                ):

                    launch_game(selected_game)

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        screen.fill(BACKGROUND)

        for x in range(30, WIDTH, 50):
            pygame.draw.line(screen, (17, 23, 42), (x, 0), (x, HEIGHT), 1)

        pygame.draw.circle(screen, (24, 36, 63), (45, 45), 8)
        pygame.draw.circle(screen, (74, 44, 93), (955, 100), 12)
        pygame.draw.circle(screen, (30, 77, 88), (945, 650), 7)

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        draw_centered_text(
            "ARCADE 2.0",
            TITLE_FONT,
            WHITE,
            24
        )

        draw_centered_text(
            "SELECT A GAME  •  CHASE THE HIGH SCORE",
            SMALL_FONT,
            GRAY,
            105
        )

        draw_centered_text(
            "HALL OF FAME",
            SUBTITLE_FONT,
            YELLOW,
            145
        )

        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            DARK_PANEL,
            (65, 185, 870, 295),
            border_radius=22,
        )
        pygame.draw.rect(
            screen,
            (48, 62, 91),
            (65, 185, 870, 295),
            width=2,
            border_radius=22,
        )

        # Header

        header_game = SMALL_FONT.render(
            "ARCADE GAME",
            True,
            GRAY
        )

        header_score = SMALL_FONT.render(
            "PERSONAL BEST",
            True,
            GRAY
        )

        screen.blit(
            header_game,
            (190, 204)
        )

        screen.blit(
            header_score,
            (720, 204)
        )

        # ----------------------------------------------------
        # GAME LIST
        # ----------------------------------------------------

        y = 238

        for number in range(1, 5):

            game_name = GAMES[number]["name"]

            score = scores[number]

            draw_game_row(
                number,
                game_name,
                score,
                y,
                selected_game == number
            )

            y += 56

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        draw_centered_text(
            "↑ / ↓  SELECT       ENTER  LAUNCH",
            SMALL_FONT,
            WHITE,
            525
        )

        draw_centered_text(
            "1–4 QUICK LAUNCH       Q / ESC EXIT",
            SMALL_FONT,
            GRAY,
            555
        )

        # ----------------------------------------------------
        # TOTAL SCORE
        # ----------------------------------------------------

        total_score = sum(scores.values())

        draw_centered_text(
            f"TOTAL ARCADE SCORE     {total_score}",
            SCORE_FONT,
            PURPLE,
            610
        )

        # ----------------------------------------------------
        # UPDATE DISPLAY
        # ----------------------------------------------------

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

    sys.exit()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()
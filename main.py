import pygame
import sys
import math
import array

pygame.init()

# ---------------- SOUND ----------------
sound_enabled = True

try:
    pygame.mixer.init()
except pygame.error:
    sound_enabled = False


def create_sound(frequency, duration):
    if not sound_enabled:
        return None

    sample_rate = 44100
    samples = int(sample_rate * duration)
    buffer = array.array("h")

    for i in range(samples):
        value = int(
            16000 * math.sin(
                2 * math.pi * frequency * i / sample_rate
            )
        )
        buffer.append(value)

    return pygame.mixer.Sound(buffer=buffer)


paddle_sound = create_sound(600, 0.08)
wall_sound = create_sound(400, 0.08)
score_sound = create_sound(200, 0.20)


def play_sound(sound):
    if sound is not None:
        sound.play()


# ---------------- WINDOW ----------------
WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - Hackathon Project")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# ---------------- PADDLES ----------------
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

left_paddle = pygame.Rect(
    30,
    HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

right_paddle = pygame.Rect(
    WIDTH - 45,
    HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)


# ---------------- BALL ----------------
BALL_SIZE = 20

ball = pygame.Rect(
    WIDTH // 2 - BALL_SIZE // 2,
    HEIGHT // 2 - BALL_SIZE // 2,
    BALL_SIZE,
    BALL_SIZE
)

BASE_SPEED = 5
SPEED_INCREASE = 0.5

ball_x_speed = BASE_SPEED
ball_y_speed = BASE_SPEED


# ---------------- SCORE ----------------
left_score = 0
right_score = 0

WINNING_SCORE = 5

high_score = 0


# ---------------- LEVEL ----------------
level = 1
MAX_LEVEL = 6


# ---------------- GAME STATES ----------------
START = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3

game_state = START


# ---------------- FONTS ----------------
title_font = pygame.font.Font(None, 90)
score_font = pygame.font.Font(None, 60)
game_over_font = pygame.font.Font(None, 70)
instruction_font = pygame.font.Font(None, 40)
level_font = pygame.font.Font(None, 35)
small_font = pygame.font.Font(None, 25)


# ---------------- RESET GAME ----------------
def reset_game():

    global left_score
    global right_score
    global ball_x_speed
    global ball_y_speed
    global level

    left_score = 0
    right_score = 0

    level = 1

    left_paddle.center = (
        30 + PADDLE_WIDTH // 2,
        HEIGHT // 2
    )

    right_paddle.center = (
        WIDTH - 45 + PADDLE_WIDTH // 2,
        HEIGHT // 2
    )

    ball.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    ball_x_speed = BASE_SPEED
    ball_y_speed = BASE_SPEED


# ---------------- RESET BALL ----------------
def reset_ball(direction):

    global ball_x_speed
    global ball_y_speed
    global level

    ball.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    total_score = left_score + right_score

    level = min(
        total_score + 1,
        MAX_LEVEL
    )

    current_speed = (
        BASE_SPEED
        + (level - 1) * SPEED_INCREASE
    )

    ball_x_speed = current_speed * direction
    ball_y_speed = current_speed


# ---------------- MAIN LOOP ----------------
running = True

while running:

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # START SCREEN
        if game_state == START:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    reset_game()

                    game_state = PLAYING

        # PLAYING
        elif game_state == PLAYING:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    game_state = PAUSED

        # PAUSED
        elif game_state == PAUSED:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    game_state = PLAYING

        # GAME OVER
        elif game_state == GAME_OVER:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    reset_game()

                    game_state = START


    # =================================================
    # PLAYING
    # =================================================

    if game_state == PLAYING:

        keys = pygame.key.get_pressed()

        # PLAYER 1
        if keys[pygame.K_w]:
            left_paddle.y -= PADDLE_SPEED

        if keys[pygame.K_s]:
            left_paddle.y += PADDLE_SPEED

        # PLAYER 2
        if keys[pygame.K_UP]:
            right_paddle.y -= PADDLE_SPEED

        if keys[pygame.K_DOWN]:
            right_paddle.y += PADDLE_SPEED


        # Keep paddles inside screen
        if left_paddle.top < 0:
            left_paddle.top = 0

        if left_paddle.bottom > HEIGHT:
            left_paddle.bottom = HEIGHT

        if right_paddle.top < 0:
            right_paddle.top = 0

        if right_paddle.bottom > HEIGHT:
            right_paddle.bottom = HEIGHT


        # Move ball
        ball.x += ball_x_speed
        ball.y += ball_y_speed


        # Wall collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:

            ball_y_speed *= -1

            play_sound(wall_sound)


        # Left paddle collision
        if (
            ball.colliderect(left_paddle)
            and ball_x_speed < 0
        ):

            ball_x_speed *= -1

            play_sound(paddle_sound)


        # Right paddle collision
        if (
            ball.colliderect(right_paddle)
            and ball_x_speed > 0
        ):

            ball_x_speed *= -1

            play_sound(paddle_sound)


        # Right player scores
        if ball.right < 0:

            right_score += 1

            play_sound(score_sound)

            if right_score > high_score:
                high_score = right_score

            if right_score >= WINNING_SCORE:

                game_state = GAME_OVER

            else:

                reset_ball(1)


        # Left player scores
        if ball.left > WIDTH:

            left_score += 1

            play_sound(score_sound)

            if left_score > high_score:
                high_score = left_score

            if left_score >= WINNING_SCORE:

                game_state = GAME_OVER

            else:

                reset_ball(-1)


    # =================================================
    # DRAW SCREEN
    # =================================================

    screen.fill(BLACK)


    # =================================================
    # START SCREEN
    # =================================================

    if game_state == START:

        title = title_font.render(
            "PONG",
            True,
            WHITE
        )

        subtitle = instruction_font.render(
            "CLASSIC ARCADE GAME",
            True,
            WHITE
        )

        controls = instruction_font.render(
            "PLAYER 1: W / S",
            True,
            WHITE
        )

        controls2 = instruction_font.render(
            "PLAYER 2: UP / DOWN",
            True,
            WHITE
        )

        start_text = instruction_font.render(
            "PRESS SPACE TO START",
            True,
            WHITE
        )

        high_score_text = instruction_font.render(
            f"HIGH SCORE: {high_score}",
            True,
            WHITE
        )


        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                50
            )
        )

        screen.blit(
            subtitle,
            (
                WIDTH // 2 - subtitle.get_width() // 2,
                140
            )
        )

        screen.blit(
            controls,
            (
                WIDTH // 2 - controls.get_width() // 2,
                210
            )
        )

        screen.blit(
            controls2,
            (
                WIDTH // 2 - controls2.get_width() // 2,
                260
            )
        )

        screen.blit(
            high_score_text,
            (
                WIDTH // 2 - high_score_text.get_width() // 2,
                320
            )
        )

        screen.blit(
            start_text,
            (
                WIDTH // 2 - start_text.get_width() // 2,
                400
            )
        )


    # =================================================
    # PLAYING SCREEN
    # =================================================

    elif game_state == PLAYING:

        # Center line
        for y in range(0, HEIGHT, 30):

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    WIDTH // 2 - 2,
                    y,
                    4,
                    15
                )
            )


        # Paddles
        pygame.draw.rect(
            screen,
            WHITE,
            left_paddle
        )

        pygame.draw.rect(
            screen,
            WHITE,
            right_paddle
        )


        # Ball
        pygame.draw.ellipse(
            screen,
            WHITE,
            ball
        )


        # Scores
        left_text = score_font.render(
            str(left_score),
            True,
            WHITE
        )

        right_text = score_font.render(
            str(right_score),
            True,
            WHITE
        )


        screen.blit(
            left_text,
            (
                WIDTH // 2 - 100,
                35
            )
        )

        screen.blit(
            right_text,
            (
                WIDTH // 2 + 70,
                35
            )
        )


        # Level
        level_text = level_font.render(
            f"LEVEL {level}",
            True,
            WHITE
        )

        screen.blit(
            level_text,
            (
                WIDTH // 2 - level_text.get_width() // 2,
                10
            )
        )


        # High score
        high_text = small_font.render(
            f"HIGH SCORE: {high_score}",
            True,
            WHITE
        )

        screen.blit(
            high_text,
            (
                10,
                10
            )
        )


        # Pause instruction
        pause_text = small_font.render(
            "P = Pause",
            True,
            WHITE
        )

        screen.blit(
            pause_text,
            (
                10,
                HEIGHT - 30
            )
        )


    # =================================================
    # PAUSED SCREEN
    # =================================================

    elif game_state == PAUSED:

        pause_title = game_over_font.render(
            "GAME PAUSED",
            True,
            WHITE
        )

        resume_text = instruction_font.render(
            "PRESS P TO RESUME",
            True,
            WHITE
        )

        paused_score = instruction_font.render(
            f"SCORE: {left_score} - {right_score}",
            True,
            WHITE
        )


        screen.blit(
            pause_title,
            (
                WIDTH // 2 - pause_title.get_width() // 2,
                150
            )
        )

        screen.blit(
            resume_text,
            (
                WIDTH // 2 - resume_text.get_width() // 2,
                260
            )
        )

        screen.blit(
            paused_score,
            (
                WIDTH // 2 - paused_score.get_width() // 2,
                330
            )
        )


    # =================================================
    # GAME OVER
    # =================================================

    elif game_state == GAME_OVER:

        if left_score >= WINNING_SCORE:

            winner_text = game_over_font.render(
                "PLAYER 1 WINS!",
                True,
                WHITE
            )

        else:

            winner_text = game_over_font.render(
                "PLAYER 2 WINS!",
                True,
                WHITE
            )


        final_score = instruction_font.render(
            f"FINAL SCORE: {left_score} - {right_score}",
            True,
            WHITE
        )

        final_level = instruction_font.render(
            f"REACHED LEVEL {level}",
            True,
            WHITE
        )

        high_score_final = instruction_font.render(
            f"HIGH SCORE: {high_score}",
            True,
            WHITE
        )

        restart_text = instruction_font.render(
            "PRESS R TO RESTART",
            True,
            WHITE
        )


        screen.blit(
            winner_text,
            (
                WIDTH // 2 - winner_text.get_width() // 2,
                90
            )
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2 - final_score.get_width() // 2,
                190
            )
        )

        screen.blit(
            final_level,
            (
                WIDTH // 2 - final_level.get_width() // 2,
                240
            )
        )

        screen.blit(
            high_score_final,
            (
                WIDTH // 2 - high_score_final.get_width() // 2,
                290
            )
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                370
            )
        )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()
import pygame
import random
import os

pygame.init()

WIDTH = 600
HEIGHT = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

SNAKE_SIZE = 20
speed = 20

font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 70)
game_over_font = pygame.font.Font(None, 65)
small_font = pygame.font.Font(None, 28)

clock = pygame.time.Clock()

# =========================
# HIGH SCORE FILE
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")


# =========================
# LOAD HIGH SCORE
# =========================

def load_high_score():

    if os.path.exists(HIGH_SCORE_FILE):

        try:

            with open(HIGH_SCORE_FILE, "r") as file:
                return int(file.read())

        except:

            return 0

    return 0


# =========================
# SAVE HIGH SCORE
# =========================

def save_high_score(high_score):

    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(high_score))


# =========================
# CREATE FOOD
# =========================

def create_food(snake):

    while True:

        food_x = random.randrange(
            0,
            WIDTH,
            SNAKE_SIZE
        )

        food_y = random.randrange(
            0,
            HEIGHT,
            SNAKE_SIZE
        )

        if [food_x, food_y] not in snake:

            return food_x, food_y


# =========================
# RESET GAME
# =========================

def reset_game():

    snake = [[300, 200]]

    direction = "RIGHT"

    food_x, food_y = create_food(snake)

    score = 0

    return snake, direction, food_x, food_y, score


snake, direction, food_x, food_y, score = reset_game()

high_score = load_high_score()

running = True
game_started = False
game_over = False
paused = False


# =========================
# MAIN GAME LOOP
# =========================

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # =========================
            # START SCREEN
            # =========================

            if not game_started:

                if event.key == pygame.K_SPACE:

                    game_started = True

            # =========================
            # GAME CONTROLS
            # =========================

            elif not game_over:

                if event.key == pygame.K_p:

                    paused = not paused

                if not paused:

                    if (
                        event.key == pygame.K_LEFT
                        and direction != "RIGHT"
                    ):

                        direction = "LEFT"

                    if (
                        event.key == pygame.K_RIGHT
                        and direction != "LEFT"
                    ):

                        direction = "RIGHT"

                    if (
                        event.key == pygame.K_UP
                        and direction != "DOWN"
                    ):

                        direction = "UP"

                    if (
                        event.key == pygame.K_DOWN
                        and direction != "UP"
                    ):

                        direction = "DOWN"

            # =========================
            # RESTART
            # =========================

            else:

                if event.key == pygame.K_r:

                    snake, direction, food_x, food_y, score = reset_game()

                    game_over = False
                    paused = False


    # =========================
    # BACKGROUND
    # =========================

    screen.fill((20, 20, 20))


    # =========================
    # GRID
    # =========================

    for x in range(0, WIDTH, SNAKE_SIZE):

        pygame.draw.line(
            screen,
            (60, 60, 60),
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, SNAKE_SIZE):

        pygame.draw.line(
            screen,
            (60, 60, 60),
            (0, y),
            (WIDTH, y)
        )


    # =========================
    # START SCREEN
    # =========================

    if not game_started:

        title_text = title_font.render(
            "SNAKE GAME",
            True,
            (0, 255, 0)
        )

        instructions_title = font.render(
            "HOW TO PLAY",
            True,
            (255, 255, 0)
        )

        move_text = small_font.render(
            "Arrow Keys  -  Move Snake",
            True,
            (255, 255, 255)
        )

        pause_text = small_font.render(
            "P  -  Pause / Resume",
            True,
            (255, 255, 255)
        )

        restart_text = small_font.render(
            "R  -  Restart after Game Over",
            True,
            (255, 255, 255)
        )

        start_text = font.render(
            "Press SPACE to Start",
            True,
            (0, 255, 0)
        )

        screen.blit(
            title_text,
            (180, 55)
        )

        screen.blit(
            instructions_title,
            (220, 130)
        )

        screen.blit(
            move_text,
            (185, 170)
        )

        screen.blit(
            pause_text,
            (205, 205)
        )

        screen.blit(
            restart_text,
            (155, 240)
        )

        screen.blit(
            start_text,
            (190, 310)
        )


    # =========================
    # GAME
    # =========================

    else:

        # =========================
        # MOVE SNAKE
        # =========================

        if not game_over and not paused:

            head_x = snake[0][0]
            head_y = snake[0][1]

            if direction == "LEFT":

                head_x -= speed

            if direction == "RIGHT":

                head_x += speed

            if direction == "UP":

                head_y -= speed

            if direction == "DOWN":

                head_y += speed

            new_head = [head_x, head_y]

            snake.insert(0, new_head)


            # =========================
            # WALL COLLISION
            # =========================

            if (
                head_x < 0
                or head_x >= WIDTH
                or head_y < 0
                or head_y >= HEIGHT
            ):

                game_over = True


            # =========================
            # BODY COLLISION
            # =========================

            if new_head in snake[1:]:

                game_over = True


            # =========================
            # FOOD COLLISION
            # =========================

            if head_x == food_x and head_y == food_y:

                score += 1

                if score > high_score:

                    high_score = score

                    save_high_score(high_score)

                food_x, food_y = create_food(snake)

            else:

                snake.pop()


        # =========================
        # SCORE
        # =========================

        score_text = font.render(
            "Score: " + str(score),
            True,
            (255, 255, 255)
        )

        screen.blit(
            score_text,
            (10, 10)
        )


        # =========================
        # HIGH SCORE
        # =========================

        high_score_text = font.render(
            "High Score: " + str(high_score),
            True,
            (255, 255, 0)
        )

        screen.blit(
            high_score_text,
            (10, 42)
        )


        # =========================
        # DIFFICULTY
        # =========================

        if score < 5:

            difficulty = "EASY"

        elif score < 10:

            difficulty = "MEDIUM"

        else:

            difficulty = "HARD"


        difficulty_text = font.render(
            "Difficulty: " + difficulty,
            True,
            (255, 255, 255)
        )

        screen.blit(
            difficulty_text,
            (400, 10)
        )


        # =========================
        # DRAW SNAKE
        # =========================

        for i, part in enumerate(snake):

            x = part[0]
            y = part[1]


            # =========================
            # SNAKE HEAD
            # =========================

            if i == 0:

                pygame.draw.rect(
                    screen,
                    (0, 220, 0),
                    (
                        x,
                        y,
                        SNAKE_SIZE,
                        SNAKE_SIZE
                    ),
                    border_radius=6
                )


                # =========================
                # EYES
                # =========================

                if direction == "RIGHT":

                    eye1 = (x + 14, y + 5)
                    eye2 = (x + 14, y + 14)

                elif direction == "LEFT":

                    eye1 = (x + 5, y + 5)
                    eye2 = (x + 5, y + 14)

                elif direction == "UP":

                    eye1 = (x + 5, y + 5)
                    eye2 = (x + 14, y + 5)

                else:

                    eye1 = (x + 5, y + 14)
                    eye2 = (x + 14, y + 14)


                pygame.draw.circle(
                    screen,
                    (255, 255, 255),
                    eye1,
                    3
                )

                pygame.draw.circle(
                    screen,
                    (255, 255, 255),
                    eye2,
                    3
                )

                pygame.draw.circle(
                    screen,
                    (0, 0, 0),
                    eye1,
                    1
                )

                pygame.draw.circle(
                    screen,
                    (0, 0, 0),
                    eye2,
                    1
                )


            # =========================
            # SNAKE BODY
            # =========================

            else:

                pygame.draw.rect(
                    screen,
                    (0, 180, 0),
                    (
                        x,
                        y,
                        SNAKE_SIZE,
                        SNAKE_SIZE
                    ),
                    border_radius=5
                )


        # =========================
        # DRAW FOOD
        # =========================

        food_center = (
            food_x + SNAKE_SIZE // 2,
            food_y + SNAKE_SIZE // 2
        )

        pygame.draw.circle(
            screen,
            (255, 0, 0),
            food_center,
            8
        )


        # =========================
        # PAUSE
        # =========================

        if paused:

            pause_message = font.render(
                "PAUSED - Press P to Continue",
                True,
                (255, 255, 255)
            )

            screen.blit(
                pause_message,
                (150, 180)
            )


        # =========================
        # GAME OVER
        # =========================

        if game_over:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(180)

            overlay.fill((0, 0, 0))

            screen.blit(
                overlay,
                (0, 0)
            )


            game_over_message = game_over_font.render(
                "GAME OVER",
                True,
                (255, 60, 60)
            )

            screen.blit(
                game_over_message,
                (185, 90)
            )


            final_score_message = font.render(
                "Final Score: " + str(score),
                True,
                (255, 255, 255)
            )

            screen.blit(
                final_score_message,
                (215, 170)
            )


            final_high_score_message = font.render(
                "High Score: " + str(high_score),
                True,
                (255, 255, 0)
            )

            screen.blit(
                final_high_score_message,
                (215, 210)
            )


            restart_message = small_font.render(
                "Press R to Restart",
                True,
                (0, 255, 0)
            )

            screen.blit(
                restart_message,
                (215, 270)
            )


    pygame.display.update()


    # =========================
    # INCREASING DIFFICULTY
    # =========================

    if game_started and not game_over and not paused:

        clock.tick(5 + score)

    else:

        clock.tick(30)


pygame.quit()
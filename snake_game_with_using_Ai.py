import pygame
import random
import sys
import os

WIDTH = 720
HEIGHT = 480
CELL_SIZE = 24

assert WIDTH % CELL_SIZE == 0 and HEIGHT % CELL_SIZE == 0
CELL_WIDTH = WIDTH // CELL_SIZE
CELL_HEIGHT = HEIGHT // CELL_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

HIGHSCORE_FILE = 'snake_highscore.txt'


def load_highscore():
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(score))
    except Exception:
        pass


def draw_grid(surface):
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, (30, 30, 30), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, (30, 30, 30), (0, y), (WIDTH, y))


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 22)
        self.title_font = pygame.font.SysFont('consolas', 48, bold=True)
        self.highscore = load_highscore()
        self.state = 'menu'  # 'menu', 'playing', 'paused', 'gameover'
        self.reset()

    def reset(self):
        self.direction = RIGHT
        start_x = CELL_WIDTH // 2
        start_y = CELL_HEIGHT // 2
        self.snake = [(start_x - i, start_y) for i in range(4)]
        self.next_direction = self.direction
        self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            pos = (random.randrange(0, CELL_WIDTH), random.randrange(0, CELL_HEIGHT))
            if pos not in self.snake:
                self.food = pos
                return

    def start(self):
        self.reset()
        self.state = 'playing'

    def toggle_pause(self):
        if self.state == 'playing':
            self.state = 'paused'
        elif self.state == 'paused':
            self.state = 'playing'

    def handle_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            candidate = UP
        elif key in (pygame.K_DOWN, pygame.K_s):
            candidate = DOWN
        elif key in (pygame.K_LEFT, pygame.K_a):
            candidate = LEFT
        elif key in (pygame.K_RIGHT, pygame.K_d):
            candidate = RIGHT
        else:
            return

        # prevent reversing
        if (candidate[0] * -1, candidate[1] * -1) == self.direction:
            return
        # buffer next direction until the next update
        self.next_direction = candidate

    def update(self):
        if self.state != 'playing':
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if not (0 <= new_head[0] < CELL_WIDTH and 0 <= new_head[1] < CELL_HEIGHT):
            self.game_over = True
            self.state = 'gameover'
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            self.state = 'gameover'
            return

        self.snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            self.snake.pop()

    def draw_hud(self):
        score_surf = self.font.render(f'Score: {self.score}', True, (240, 240, 240))
        hs_surf = self.font.render(f'Best: {self.highscore}', True, (200, 200, 200))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(hs_surf, (10, 34))

    def draw(self):
        # background
        self.screen.fill((12, 12, 12))
        draw_grid(self.screen)

        # draw food
        fx, fy = self.food
        food_rect = pygame.Rect(fx * CELL_SIZE + 3, fy * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6)
        pygame.draw.rect(self.screen, (220, 60, 60), food_rect, border_radius=6)

        # draw snake
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            if i == 0:
                pygame.draw.rect(self.screen, (90, 220, 90), rect, border_radius=6)
            else:
                pygame.draw.rect(self.screen, (40, 180, 40), rect, border_radius=6)

        # HUD
        self.draw_hud()

        if self.state == 'paused':
            pause_surf = self.title_font.render('Paused', True, (255, 215, 0))
            rect = pause_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(pause_surf, rect)

        if self.state == 'gameover':
            go_font = self.title_font
            go_surf = go_font.render('Game Over', True, (255, 80, 80))
            rect = go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(go_surf, rect)

            info = self.font.render('Press R to restart or M for menu', True, (220, 220, 220))
            info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.screen.blit(info, info_rect)

        pygame.display.flip()

    def draw_menu(self):
        self.screen.fill((8, 10, 15))
        title = self.title_font.render('Snake', True, (120, 255, 160))
        rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title, rect)

        start = self.font.render('Press ENTER to start', True, (200, 200, 200))
        h = self.font.render('High Score: ' + str(self.highscore), True, (180, 180, 180))
        inst = self.font.render('Arrows / WASD to move — P / Space to pause', True, (140, 140, 140))

        self.screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
        self.screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 36))
        self.screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT // 2 + 72))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN:
                        self.start()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                elif self.state == 'playing':
                    if event.key in (pygame.K_p, pygame.K_SPACE):
                        self.toggle_pause()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    else:
                        self.handle_key(event.key)
                elif self.state == 'paused':
                    if event.key in (pygame.K_p, pygame.K_SPACE):
                        self.toggle_pause()
                elif self.state == 'gameover':
                    if event.key == pygame.K_r:
                        # check highscore
                        if self.score > self.highscore:
                            self.highscore = self.score
                            save_highscore(self.highscore)
                        self.start()
                    elif event.key == pygame.K_m:
                        if self.score > self.highscore:
                            self.highscore = self.score
                            save_highscore(self.highscore)
                        self.state = 'menu'

    def run(self):
        while True:
            self.handle_events()

            if self.state == 'menu':
                self.draw_menu()
                self.clock.tick(30)
                continue

            if self.state == 'playing':
                self.update()

            self.draw()
            # speed scales with score but capped
            fps = min(30, 8 + 2 * (1 + self.score // 3))
            self.clock.tick(fps)

        


if __name__ == '__main__':
    SnakeGame().run()
    















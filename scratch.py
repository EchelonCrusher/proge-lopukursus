import pygame
import random


SCREEN_WIDTH = 920
SCREEN_HEIGHT = 920

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.length = 10
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last_direction = self.direction
        self.color = (0, 255, 0)
        self.head_sprite = pygame.image.load('./kivi2.png')
        self.body_sprite = pygame.image.load('./pudel2.png')

    def get_head_position(self):
        return self.positions[0]

    def get_middle_position(self):
        try:
            return self.positions[self.length // 2]
        except IndexError:
            return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0]*-1, point[1]*-1) == self.direction: #  or (point[0]*-1, point[1]*-1) == self.last_direction:
            return
        else:
            print(point, self.last_direction, self.direction)
            self.last_direction = tuple(self.direction)
            self.direction = point

    def move(self, enemy=None):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0]+(x*GRID_SIZE)) % SCREEN_WIDTH), (cur[1]+(y*GRID_SIZE)) % SCREEN_HEIGHT)
        if len(self.positions) > 2 and new in self.positions[2:]:
            enemy.dead = True
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 10
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for index, p in enumerate(self.positions):
            if index == 0:  # head of the snake
                surface.blit(self.head_sprite, (p[0], p[1]))
            else:  # body of the snake
                surface.blit(self.body_sprite, (p[0], p[1]))


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1)*GRID_SIZE, random.randint(0, GRID_HEIGHT-1)*GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))


class Enemy:
    def __init__(self):
        self.position = (0, 0)
        self.color = (0, 255, 0)
        self.randomize_position()
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.dead = True

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1)*GRID_SIZE, random.randint(0, GRID_HEIGHT-1)*GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

    def move(self, snake):
        self.dead = False
        if random.random() < 0.8:  # 80% chance to move towards snake's middle position
            snake_middle = snake.get_middle_position()
            dx = snake_middle[0] - self.position[0]
            dy = snake_middle[1] - self.position[1]

            if random.random() < 0.5:
                self.direction = RIGHT if dx > 0 else LEFT
            else:
                self.direction = DOWN if dy > 0 else UP

        else:  # 50% chance to move randomly
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        cur = self.position
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % SCREEN_WIDTH), (cur[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        self.position = new

    def collision(self, snake):
        if self.dead:
            return
        if snake.get_head_position() == self.position:
            self.randomize_position()
            self.dead = True
        elif self.position in snake.positions:
            index = snake.positions.index(self.position)
            snake.positions = snake.positions[:index]
            snake.length = index


def draw_grid(surface):
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            if (x+y) % 2 == 0:
                r = pygame.Rect((x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, (93, 216, 228), r)
            else:
                rr = pygame.Rect((x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, (84, 194, 205), rr)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()

    snake = Snake()
    food = Food()
    enemy = Enemy()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and not movement_activated:  # Check if movement has not been activated yet
                if event.key == pygame.K_UP:
                    snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.turn(RIGHT)
                movement_activated = True  # Set movement_activated to True after movement is activated

        if not enemy.dead and random.random() < 0.4:
            enemy.move(snake)
        snake.move(enemy)
        # Reset movement_activated at the start of each tick
        movement_activated = False

        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.move()
            food.randomize_position()
            if snake.length >= 5:
                enemy.dead = False
        enemy.collision(snake)

        draw_grid(surface)
        snake.draw(surface)
        if not enemy.dead:
            enemy.draw(surface)
        food.draw(surface)
        screen.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(10)


if __name__ == "__main__":
    main()

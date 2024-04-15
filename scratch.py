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

SHOP_ITEMS = ["XP Booster", "Wormhole", "Healing", "Armor", "Extra Apple", "Time Freeze"]
SHORT_POWERUP_TIMER = 15
LONG_POWERUP_TIMER = 30

class Snake:
    def __init__(self):
        self.length = 10
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last_direction = self.direction
        self.color = (0, 255, 0)
        self.head_sprite = pygame.image.load('./kivi2.png')
        self.body_sprite = pygame.image.load('./pudel2.png')
        self.xp = 0
        self.lvl = 1
        self.xp_for_next_lvl = 30
        self.xp_curve_start_lvl = 5

    def level_up(self):
        if self.xp == self.xp_for_next_lvl:
            self.lvl += 1
            self.xp = 0
            if self.lvl >= self.xp_curve_start_lvl:
                self.xp_for_next_lvl += 5

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


def spawn(count=1):
    fireballs = []
    for i in range(count):
        fireball = Fireball()
        fireballs.append(fireball)
    return fireballs


class Fireball:
    def __init__(self):
        self.position = (0, 0)
        self.color = (242, 195, 65)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.randomize_position()
        self.tick = 0

    def randomize_position(self):
        x, y = self.direction
        if x == 0:
            y_coord = (GRID_HEIGHT - 1) * (y == -1) # (0, 1) is down, (0, -1) is up
            self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, y_coord * GRID_SIZE)
        else:
            x_coord = (GRID_WIDTH - 1) * (x == -1) # (1, 0) is right, (-1, 0) is left
            self.position = (x_coord * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

    def move(self, snake):
        if self.collision(snake):
            return True
        if self.tick < 3:  # Movement every 3 ticks
            self.tick += 1
            return
        self.tick = 0
        cur = self.position
        x, y = self.direction
        self.position = (((cur[0] + (x * GRID_SIZE)) % SCREEN_WIDTH), (cur[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        self.collision(snake)

    def collision(self, snake):
        if snake.get_head_position() == self.position:
            snake.reset()
            return True
        elif self.position in snake.positions:
            index = snake.positions.index(self.position)
            snake.positions = snake.positions[:index]
            snake.length = index


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
        else:  # 20% chance to move randomly
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        cur = self.position
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % SCREEN_WIDTH), (cur[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        self.collision(snake)
        # if new == snake.get_head_position:  # Check for collision
        #     return
        self.position = new

    def collision(self, snake):
        if self.dead:
            return
        if snake.get_head_position() == self.position:
            self.randomize_position()
            self.dead = True
            snake.xp += 10
        elif self.position in snake.positions:
            index = snake.positions.index(self.position)
            snake.positions = snake.positions[:index]
            snake.length = index


def draw_grid(surface):
    center_x = GRID_WIDTH // 2
    center_y = GRID_HEIGHT // 2
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            distance_x = abs(x - center_x)
            distance_y = abs(y - center_y)
            distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

            # Calculate color components based on distance
            red = 93  # + distance * 8  # Increase red content by 5 per grid size away from the center
            blue = 228  # - distance * 8  # Decrease blue content by 5 per grid size away from the center

            # Ensure color components stay within range [0, 255]
            red = max(0, min(red, 255))
            blue = max(0, min(blue, 255))

            # Draw rectangles with modified colors
            if (x + y) % 2 == 0:
                color = (red, 216, blue)
            else:
                color = (red - 9, 194, blue + 11)  # Adjusting green component to maintain contrast
            r = pygame.Rect((x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, r)

def main():
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    # XP counter
    font_size = 32
    font = pygame.font.Font(None, font_size)
    xpcounter_x = 20
    xpcounter_y = 20

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()

    snake = Snake()
    food = Food()
    enemy = Enemy()
    fireballs = []
    fireballs += spawn(6)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and not movement_disabled:  # Check if movement is allowed
                if event.key == pygame.K_UP:
                    snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.turn(RIGHT)
                movement_disabled = True  # Disable movement

        snake.move(enemy)
        if not enemy.dead and random.random() < 0.4:
            enemy.move(snake)
        # Enable movement
        movement_disabled = False

        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.move()
            snake.xp += 5
            food.randomize_position()
            if snake.length >= 5:
                enemy.dead = False
        enemy.collision(snake)
        for fireball in fireballs:
            if fireball.move(snake):  # If collision is True
                fireballs.remove(fireball)
                snake.xp = 0
        draw_grid(surface)
        snake.draw(surface)
        for fireball in fireballs:
            fireball.draw(surface)
        if not enemy.dead:
            enemy.draw(surface)
        food.draw(surface)
        screen.blit(surface, (0, 0))
        clock.tick(10)

        # Render the text
        text = font.render(str(snake.xp), True, (0, 255, 0), (0, 0, 0))

        # Seda recti on vist ainult ühe korra vaja teha
        textRect = text.get_rect() # Get the rect of the text
        textRect.topleft = (xpcounter_x, xpcounter_y) # Position the text

        surface.blit(text, textRect) # Blit the text onto the existing game surface
        screen.blit(surface, (0, 0)) # Blit the game surface onto the screen
        pygame.display.update() # Update the display


if __name__ == "__main__":
    main()

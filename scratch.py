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

font_size = 32
text_x = 20
text_y = 20
text_color = (255, 255, 255)  # Text color
outline_color = (0, 0, 0)  # Outline color
outline_width = 1.5  # Outline width

global SNAKE
global ENEMY

shop_items = ["XP Booster", "Wormhole", "Healing", "Armor", "Extra Apple", "Time Freeze"]
short_powerup_timer = 15
long_powerup_timer = 30


class Snake:
    def __init__(self):
        self.length = 10
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = (0, 255, 0)
        self.head_sprite = pygame.transform.scale(pygame.image.load('./head.png'), (20, 20))
        self.body_sprite = pygame.transform.scale(pygame.image.load('./body.png'), (20, 20))
        self.end_sprite = pygame.transform.scale(pygame.image.load('./end.png'), (20, 20))
        self.xp = 0
        self.level = 0
        self.needed_xp = 5
        self.level_up_sound = pygame.mixer.Sound('level_up.mp3')

    def get_head_position(self):
        return self.positions[0]

    def get_middle_position(self):
        try:
            return self.positions[self.length // 2]
        except IndexError:
            return self.positions[0]

    def turn(self, direction):
        if self.length > 1 and (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        else:
            self.direction = direction

    def move(self):
        pos = self.get_head_position()
        x, y = self.direction
        # Moves the player one grid forward, wrapping to the opposite side of the screen if it reaches the edge
        new_pos = (((pos[0]+(x*GRID_SIZE)) % SCREEN_WIDTH), (pos[1]+(y*GRID_SIZE)) % SCREEN_HEIGHT)
        if len(self.positions) > 2 and new_pos in self.positions[2:]:  # Player runs into themselves
            self.reset()
        else:
            self.positions.insert(0, new_pos)
            if len(self.positions) > self.length:  # Removes positions exceeding max length
                self.positions.pop()

    def reset(self):
        self.length = 10
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.xp = 0
        self.level = 0
        self.needed_xp = 5
        # Remove boss state, reset fireballs

    def draw(self, surface):
        for index, p in enumerate(self.positions):
            if index == 0:  # Head piece
                self.edge_pieces(p, surface, self.head_sprite, self.direction)
            elif index == len(self.positions) - 1:  # End piece
                direction_between = ((self.positions[-2][0] - p[0]) / 20, (self.positions[-2][1] - p[1]) / 20)
                self.edge_pieces(p, surface, self.end_sprite, direction_between)
            else:  # body of the snake
                surface.blit(self.body_sprite, (p[0], p[1]))

    def edge_pieces(self, p, surface, sprite, direction):  # head.png and end.png rotation
        rotated_head_sprite = pygame.transform.rotate(sprite, self.angle(direction))
        # Get the position to blit the sprite
        head_rect = rotated_head_sprite.get_rect(center=(p[0] + GRID_SIZE / 2, p[1] + GRID_SIZE / 2))
        surface.blit(rotated_head_sprite, head_rect)

    def angle(self, direction):  # Calculate rotation angle based on direction
        if direction == UP:
            return 180
        elif direction == DOWN:
            return 0
        elif direction == LEFT:
            return -90
        elif direction == RIGHT:
            return 90
        else:
            return self.angle(self.direction)

    def experience(self, amount: int):
        self.xp += amount
        if self.xp >= self.needed_xp:
            self.level_up_sound.play()
            self.level += 1
            self.xp -= self.needed_xp
            self.needed_xp += 2
            self.experience(0)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 0, 0)
        self.randomize_position()
        self.sprite = pygame.transform.scale(pygame.image.load('./apple.png'), (20, 20))

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1)*GRID_SIZE, random.randint(0, GRID_HEIGHT-1)*GRID_SIZE)

    def draw(self, surface):
        surface.blit(self.sprite, (self.position[0], self.position[1]))


def spawn(class_name: str, count=1):
    objs = []
    for i in range(count):
        if class_name == "Fireball":
            obj = Fireball()
            objs.append(obj)
        elif class_name == "Enemy":
            obj = Enemy()
            objs.append(obj)
    return objs


class Fireball:
    def __init__(self):
        self.position = (0, 0)
        self.color = (242, 195, 65)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.randomize_position()
        self.tick = 0
        self.kill = False
        global SNAKE

    def randomize_position(self):
        x, y = self.direction
        if x == 0:
            y_coord = (GRID_HEIGHT - 1) * (y == -1)  # down and up
            self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE, y_coord * GRID_SIZE)
        else:
            x_coord = (GRID_WIDTH - 1) * (x == -1)  # right and left
            self.position = (x_coord * GRID_SIZE, random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

    def move(self):
        self.collision()
        if self.tick < 3:  # Movement every 3 ticks
            self.tick += 1
            return
        self.tick = 0
        pos = self.position
        x, y = self.direction
        if pos[0] > SCREEN_WIDTH or pos[0] < 0 or pos[1] > SCREEN_WIDTH or pos[1] < 0:
            self.kill = True
        self.position = ((pos[0] + (x * GRID_SIZE)), (pos[1] + (y * GRID_SIZE)))
        self.collision()

    def collision(self):
        if SNAKE.get_head_position() == self.position:
            SNAKE.reset()
            return True
        elif self.position in SNAKE.positions:
            index = SNAKE.positions.index(self.position)
            SNAKE.positions = SNAKE.positions[:index]
            SNAKE.length = index
            self.kill = True


class Enemy:
    def __init__(self):
        self.position = (0, 0)
        self.color = (0, 255, 0)
        self.randomize_position()
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.dead = True
        self.nom_sound = pygame.mixer.Sound('nom.mp3')
        global SNAKE

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1)*GRID_SIZE, random.randint(0, GRID_HEIGHT-1)*GRID_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

    def move(self):
        self.dead = False
        if random.random() < 0.8:  # 80% chance to move towards snake's middle position
            snake_middle = SNAKE.get_middle_position()
            dx = snake_middle[0] - self.position[0]
            dy = snake_middle[1] - self.position[1]

            if random.random() < 0.5:
                self.direction = RIGHT if dx > 0 else LEFT
            else:
                self.direction = DOWN if dy > 0 else UP
        else:  # 20% chance to move randomly
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        pos = self.position
        x, y = self.direction
        new_pos = (((pos[0] + (x * GRID_SIZE)) % SCREEN_WIDTH), (pos[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        self.collision()
        self.position = new_pos

    def collision(self):
        if self.dead:
            return
        if SNAKE.get_head_position() == self.position:
            self.randomize_position()
            SNAKE.experience(3)
            self.nom_sound.play()
            self.dead = True
        elif self.position in SNAKE.positions:
            index = SNAKE.positions.index(self.position)
            SNAKE.positions = SNAKE.positions[:index]
            SNAKE.length = index


class Lever:
    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 255, 255)
        self.randomize_position()
        self.flicks = 0
        global SNAKE

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1)*GRID_SIZE, random.randint(0, GRID_HEIGHT-1)*GRID_SIZE)

    def collision(self):
        if SNAKE.get_head_position() == self.position:
            self.flicks += 1
            if self.flicks < 5:
                self.randomize_position()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))


def draw_grid(surface):
    colors = [[93, 216, 228], [92, 194, 228]]
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            # Draw rectangles with modified colors
            if (x + y) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]
            rectangle = pygame.Rect((x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rectangle)


def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    global SNAKE
    SNAKE = Snake()
    food = Food()
    global ENEMY
    ENEMY = Enemy()
    fireballs = []
    boss_levels = [0]
    boss_active = False
    boss_cooldown = 0
    fireball_cooldown = 15

    font = pygame.font.Font(None, font_size)
    boss_start = pygame.mixer.Sound('RageActivate.wav')
    boss_end = pygame.mixer.Sound('RageEnd.wav')
    boss_end.set_volume(0.5), boss_start.set_volume(0.5)
    nom_sound = pygame.mixer.Sound('nom.mp3')

    tick_rate = 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and not movement_disabled:
                if event.key == pygame.K_UP:
                    SNAKE.turn(UP)
                elif event.key == pygame.K_DOWN:
                    SNAKE.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    SNAKE.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    SNAKE.turn(RIGHT)
                movement_disabled = True  # Disable movement

        SNAKE.move()
        if not ENEMY.dead and random.random() < 0.4:
            ENEMY.move()
        # Enable movement
        movement_disabled = False

        if SNAKE.get_head_position() == food.position:
            SNAKE.length += 1
            SNAKE.move()
            food.randomize_position()
            SNAKE.experience(1)
            nom_sound.play()

            if SNAKE.length >= 5:
                ENEMY.dead = False
        ENEMY.collision()

        for fireball in fireballs:
            fireball.move()
            if fireball.kill:
                fireballs.remove(fireball)

        if SNAKE.level == 0 and SNAKE.xp == 0:  # Reset board upon death
            fireballs = []
            boss_levels = [0]
            tick_rate = 10
            ENEMY.dead = True
            if boss_active:
                boss_end.play()
                boss_active = False
                while pygame.mixer.get_busy():
                    pygame.time.wait(30)

        draw_grid(surface)

        if boss_active:
            lever.collision()
            fireball_cooldown -= 1
            if fireball_cooldown <= 0:
                fireball_cooldown = 15
                fireballs += spawn("Fireball", 1)

            if lever.flicks >= 1:
                boss_end.play()
                tick_rate = 10
                boss_active = False
                SNAKE.experience(max((2 * (SNAKE.length - 2)), 2))
            else:
                lever.draw(surface)

        elif boss_cooldown > 0:
            boss_cooldown -= 1

        SNAKE.draw(surface)
        for fireball in fireballs:
            fireball.draw(surface)
        if not ENEMY.dead:
            ENEMY.draw(surface)
        food.draw(surface)
        screen.blit(surface, (0, 0))
        display_ui(font, screen)

        # Activate boss battle
        if SNAKE.level % 3 == 0 and SNAKE.level not in boss_levels:
            boss_levels.append(SNAKE.level)
            if boss_cooldown <= 0:
                boss_cooldown = 100
                boss_start.play()
                tick_rate = 15
                fireballs += spawn("Fireball", 10)
                if not boss_active:
                    lever = Lever()
                    boss_active = True

        clock.tick(tick_rate)


def display_ui(font, screen):
    # XP and Level counter display
    xp_text = font.render(f"{SNAKE.xp} / {SNAKE.needed_xp}", True, text_color)
    xp_outline_text = font.render(f"{SNAKE.xp} / {SNAKE.needed_xp}", True, outline_color)

    level_text = font.render(f"Level: {SNAKE.level}", True, text_color)
    level_outline_text = font.render(f"Level: {SNAKE.level}", True, outline_color)

    # Blit outline text with offsets to create the outline effect
    for dx, dy in [(0, -outline_width), (0, outline_width), (-outline_width, 0), (outline_width, 0)]:
        screen.blit(xp_outline_text, (text_x + dx, text_y + dy))
        screen.blit(level_outline_text, (text_x + dx, text_y + xp_text.get_height() + 5 + dy))

    screen.blit(xp_text, (text_x, text_y))
    screen.blit(level_text, (text_x, text_y + xp_text.get_height() + 5))
    pygame.display.update()


if __name__ == "__main__":
    main()

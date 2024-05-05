import pygame

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)


# Function to create the shop window surface
def create_shop_window(items, selected_item):
    shop_surface = pygame.Surface((400, 300))
    shop_surface.fill(GRAY)

    # Draw white outline
    pygame.draw.rect(shop_surface, WHITE, shop_surface.get_rect(), 2)

    # Draw elements such as items and their prices
    font = pygame.font.SysFont(None, 30)
    for i, item in enumerate(items):
        text_render = font.render(item, True, BLACK)
        shop_surface.blit(text_render, (50, 50 + i * 40))
    pygame.draw.rect(shop_surface, WHITE, (30, 45 + selected_item * 40, 340, 40), 2)

    return shop_surface

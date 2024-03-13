import pygame

xp = 0
lvl = 1
xp_for_next_lvl = 30 # The amount of XP needed for the next level
xp_curve_start_lvl = 5 # The level at which the XP requirement for every new level starts rising

X = 10
Y = 10
display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption("XP Count")
font = pygame.font.Font("freesansbold.ttf", 12)
text = font.render(xp, True, green, black)

def level_up():
    if xp == xp_for_next_lvl:
        lvl += 1
        xp = 0
        if lvl >= xp_curve_start_lvl:
            xp_for_next_lvl += 5

shop_items = ["XP Booster", "Wormhole", "Healing", "Armor", "Extra Apple", "Time Freeze"]
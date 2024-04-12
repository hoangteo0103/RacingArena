import pygame
import os

ASSETS_DIR = "./assets/"
GUI_PAD = 20
GUI_BTN_PAD = 8
GUI_BTN_OUTLINE_W = 3

pygame.init()
pygame.font.init()

FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "OpenSans-Regular.ttf"), 28)
FONT_LABEL = pygame.font.Font(os.path.join(ASSETS_DIR, "OpenSans-ExtraBold.ttf"), 14)
FONT_ACCENT = pygame.font.Font(os.path.join(ASSETS_DIR, "OpenSans-SemiBold.ttf"), 28)
FONT_SMALL_ACCENT = pygame.font.Font(os.path.join(ASSETS_DIR, "OpenSans-SemiBold.ttf"), 22)
FONT_TITLE = pygame.font.Font(os.path.join(ASSETS_DIR, "OpenSans-ExtraBold.ttf"), 48)


# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
EXIT_BTN_WIDTH = 120
EXIT_BTN_HEIGHT = 40
EXIT_BTN_COLOR = (255, 0, 0)
EXIT_BTN_TEXT_COLOR = (255, 255, 255)
MAX_PLAYERS_PER_ROW = 5
PLAYER_ROW_PADDING = 50
CIRCLE_RADIUS = 30
FONT_SIZE = 24


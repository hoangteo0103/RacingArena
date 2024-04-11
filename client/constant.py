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


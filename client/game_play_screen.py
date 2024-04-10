import pygame
from pygame.locals import *

class GamePlayScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
        return True

    def draw(self, message, player_positions):
        self.screen.fill((255, 255, 255))
        # Draw game elements based on player positions, etc.
        message_text = self.font.render(message, True, (0, 0, 0))
        self.screen.blit(message_text, (100, 50))
        pygame.display.flip()

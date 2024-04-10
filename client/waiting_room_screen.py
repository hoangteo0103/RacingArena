import pygame
from pygame.locals import *

class WaitingRoomScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
        return True

    def draw(self):
        self.screen.fill((255, 255, 255))
        waiting_text = self.font.render("Waiting for other players...", True, (0, 0, 0))
        self.screen.blit(waiting_text, (200, 250))
        pygame.display.flip()

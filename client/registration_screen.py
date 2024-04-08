import pygame
from pygame.locals import *
from text_input_box import TextInputBox

class RegistrationScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.nickname_input = TextInputBox(200, 200, 400, 40, pygame.font.Font(None, 24))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            self.nickname_input.handle_event(event)
            if event.type == KEYDOWN:
                if event.key == K_RETURN and self.nickname_input.text:
                    return self.nickname_input.text
        return True

    def draw(self):
        self.screen.fill((255, 255, 255))
        nickname_text = self.font.render("Enter your nickname:", True, (0, 0, 0))
        self.screen.blit(nickname_text, (200, 150))
        self.nickname_input.update()
        self.nickname_input.draw(self.screen)
        pygame.display.flip()

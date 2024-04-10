import pygame
from pygame.locals import *
from text_input_box import TextInputBox
from button import Button

class RegistrationScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.nickname_input = TextInputBox(200, 200, 400, 40, pygame.font.Font(None, 24))
        self.enter_button = Button(350, 300, 100, 40, "Enter", pygame.font.Font(None, 24), pygame.Color('blue'), pygame.Color('dodgerblue'), self.handle_enter)

        self.enter_clicked = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            self.nickname_input.handle_event(event)
            self.enter_button.handle_event(event)
        return True

    def handle_enter(self):
        self.enter_clicked = True

    def draw(self):
        self.screen.fill((255, 255, 255))
        nickname_text = self.font.render("Enter your nickname:", True, (0, 0, 0))
        self.screen.blit(nickname_text, (200, 150))
        self.nickname_input.update()
        self.nickname_input.draw(self.screen)
        self.enter_button.draw(self.screen)
        pygame.display.flip()

    def get_nickname(self):
        if self.enter_clicked:
            return self.nickname_input.text
        else:
            return None

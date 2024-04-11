import pygame
from pygame.locals import *
from components import GuiButton
from constant import *

class MenuScreen:
    def __init__(self, screen, join_server_callback, create_server_callback, quit_callback):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        act_btn_w = 300
        self.create_server_button = GuiButton((250, 200), FONT_ACCENT.render("Join Server", True, (0, 0, 0)), min_w=act_btn_w, callback=join_server_callback)
        self.join_server_button = GuiButton((250, 300), FONT_ACCENT.render("Create Server", True, (0, 0, 0)), min_w=act_btn_w, callback=create_server_callback)
        self.quit_button = GuiButton((250, 400), FONT_ACCENT.render("Quit", True, (0, 0, 0)), min_w=act_btn_w, callback=quit_callback)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.create_server_button.update(events, mouse_pos)
        self.join_server_button.update(events, mouse_pos)
        self.quit_button.update(events, mouse_pos)

        return True

    def draw(self):
        self.screen.fill((255, 255, 255))

        title_text = self.font.render("Racing Arena Menu", True, (0, 0, 0))
        self.screen.blit(title_text, (270, 100))

        self.create_server_button.draw(self.screen)
        self.join_server_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        pygame.display.flip()

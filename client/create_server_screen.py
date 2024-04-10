import pygame
from pygame.locals import *
from components import *
from  constant import  *

class CreateServerScreen:
    def __init__(self, screen, create_callback, back_callback):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.create_callback = create_callback
        self.back_callback = back_callback

        menu_entry_w = 500
        entry_x = (WIDTH - menu_entry_w) / 2
        place_y = 50  # Adjust this as needed

        self.entry_ip = GuiEntry((entry_x, place_y), self.font, initial_text="127.0.0.1", min_w=menu_entry_w, max_length=30, _type=ENTRY_TYPE_TEXT)
        place_y += 60  # Padding
        self.entry_name = GuiEntry((entry_x, place_y), self.font, initial_text="newbie", min_w=menu_entry_w, max_length=25, _type=ENTRY_TYPE_TEXT)
        place_y += 60  # Padding

        self.btn_entry_create = GuiButton((entry_x, place_y), self.font.render("Host", True, (0, 0, 0)), min_w=menu_entry_w, callback=self.create_callback)
        place_y += 70  # Padding

        self.btn_entry_back = GuiButton((GUI_BTN_PAD, GUI_BTN_PAD), self.font.render("Back", True, (0, 0, 0)), min_w=120, callback=self.back_callback)

        self.entry_err_txt = None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        create_pressed = self.btn_entry_create.update(events, mouse_pos)
        back_pressed = self.btn_entry_back.update(events, mouse_pos)

        if create_pressed:
            # Implement create server functionality
            ip = self.entry_ip.get()
            name = self.entry_name.get()
            print("Create Server with IP:", ip, "and Name:", name)

        if back_pressed:
            self.back_callback()

        self.entry_ip.update(events, mouse_pos)
        self.entry_name.update(events, mouse_pos)

        return True

    def draw(self):
        self.screen.fill((255, 255, 255))

        title_text = self.font.render("Create Server", True, (0, 0, 0))
        self.screen.blit(title_text, (200, 20))

        self.entry_ip.draw(self.screen)
        self.entry_name.draw(self.screen)

        self.btn_entry_create.draw(self.screen)
        self.btn_entry_back.draw(self.screen)

        pygame.display.flip()

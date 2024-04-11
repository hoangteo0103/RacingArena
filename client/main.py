import pygame
from pygame.locals import *
from registration_screen import RegistrationScreen
from waiting_room_screen import WaitingRoomScreen
from game_play_screen import GamePlayScreen
from menu_screen import MenuScreen
from create_server_screen import CreateServerScreen
import socket
import threading

# Constants
HOST = 'localhost'
PORT = 12345
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)

class RacingArenaClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Racing Arena Client")

        self.current_screen = None
        self.nickname = None
        self.registration_screen = None

    def create_server_callback(self):
        print("Create Server clicked")

    def join_server_callback(self):
        print("Join Server clicked")
        # Implement join server functionality here

    def quit_callback(self):
        print("Quit clicked")
        pygame.quit()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
        if self.current_screen is None:
            return True

        if not self.current_screen.handle_events(events):
            return False

        if self.current_screen == self.registration_screen:
            if self.current_screen.get_nickname():
                self.nickname = self.current_screen.get_nickname()
                self.switch_to_waiting_room_screen()

        return True

    def switch_to_registration_screen(self):
        self.registration_screen = RegistrationScreen(self.screen)
        self.current_screen = self.registration_screen

    def switch_to_waiting_room_screen(self):
        self.waiting_room_screen = WaitingRoomScreen(self.screen)
        self.current_screen = self.waiting_room_screen

    def switch_to_game_play_screen(self):
        self.game_play_screen = GamePlayScreen(self.screen)
        self.current_screen = self.game_play_screen

    def switch_to_menu_screen(self):
        self.menu_screen = MenuScreen(self.screen, self.join_server_callback, self.switch_to_create_server_screen, self.quit_callback)
        self.current_screen = self.menu_screen

    def switch_to_create_server_screen(self):
        self.create_server_screen = CreateServerScreen(self.screen, self.create_server_callback, self.switch_to_menu_screen)
        self.current_screen = self.create_server_screen

    def run(self):
        clock = pygame.time.Clock()
        self.switch_to_menu_screen()

        while True:
            if not self.handle_events():
                break

            if self.current_screen:
                self.current_screen.draw()

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    client = RacingArenaClient()
    client.run()

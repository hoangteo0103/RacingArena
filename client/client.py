import pygame
from pygame.locals import *
from registration_screen import RegistrationScreen
from waiting_room_screen import WaitingRoomScreen
from game_play_screen import GamePlayScreen
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

    def handle_events(self):
        if self.current_screen is None:
            return True

        return self.current_screen.handle_events()

    def switch_to_registration_screen(self):
        self.current_screen = RegistrationScreen(self.screen)

    def switch_to_waiting_room_screen(self):
        self.current_screen = WaitingRoomScreen(self.screen)

    def switch_to_game_play_screen(self):
        self.current_screen = GamePlayScreen(self.screen)

    def run(self):
        clock = pygame.time.Clock()
        self.switch_to_registration_screen()

        while True:
            if not self.handle_events():
                break

            if self.nickname:
                self.switch_to_waiting_room_screen()
                # Here you can handle the waiting room logic

            if self.current_screen:
                self.current_screen.draw()

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    client = RacingArenaClient()
    client.run()

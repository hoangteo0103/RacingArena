import pygame
from pygame.locals import *
from components import *
from  constant import  *
from menu_screen import *
import socket
from server.constant import *

class WaitingRoomScreen:
    def __init__(self, screen ,client, gameplay_callback, back_callback):
        self.screen = screen
        self.client = client
        self.gameplay_callback = gameplay_callback
        self.back_callback = back_callback

        self.font = FONT_ACCENT

        menu_entry_w = 500
        entry_x = (WIDTH - menu_entry_w) / 2

        players = ["Player1", "Player2", "Player3", "Player4", "Player5",
                   "Player6", "Player7", "Player8", "Player9", "Player10"]
        self.players = players
        self.btn_entry_back = GuiButton((GUI_BTN_PAD, GUI_BTN_PAD), self.font.render("Back", True, (0, 0, 0)), min_w=120, callback=self.back_callback)

        self.clock = pygame.time.Clock()

    def server_update(self, packets):
        for packet in packets:
            pID, pDATA = packet

            if pID == PACKET_GAME_START:
                self.gameplay_callback(self.client)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        self.btn_entry_back.update(events, mouse_pos)

        return True

    def draw(self):
        self.screen.fill(WHITE)

        # Draw number of players
        num_players_text = f"{len(self.players)}/{MAX_PLAYERS_PER_ROW}"
        num_players_render = self.font.render(num_players_text, True, BLACK)

        self.screen.blit(num_players_render, (710, 10))

        # Draw player circles and nicknames
        circle_x = (self.screen.get_width() - (2 * CIRCLE_RADIUS + PLAYER_ROW_PADDING) * MAX_PLAYERS_PER_ROW) / 2
        circle_y = 100
        current_row = []
        for player in self.players:
            player_text = self.font.render(player, True, BLACK)
            if len(current_row) >= MAX_PLAYERS_PER_ROW:
                # Draw next row
                circle_y += 2 * CIRCLE_RADIUS + PLAYER_ROW_PADDING
                current_row = []
                circle_x = (self.screen.get_width() - (2 * CIRCLE_RADIUS + PLAYER_ROW_PADDING) * MAX_PLAYERS_PER_ROW) / 2

            pygame.draw.circle(self.screen, GREEN, (int(circle_x) + CIRCLE_RADIUS, circle_y + CIRCLE_RADIUS), CIRCLE_RADIUS)
            self.screen.blit(player_text, (int(circle_x) + CIRCLE_RADIUS - player_text.get_width() // 2, circle_y + 2 * CIRCLE_RADIUS + 10))
            current_row.append(player)
            circle_x += 2 * CIRCLE_RADIUS + PLAYER_ROW_PADDING

        self.btn_entry_back.draw(self.screen)


        pygame.display.flip()
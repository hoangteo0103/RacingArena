import pygame
import sys
import time
from pygame.locals import *
from components import *
from constant import *
from server.constant import *
class GamePlayScreen:
    def __init__(self, screen, client):
        self.client = client
        self.screen = screen

        question = "What is 5 + 3?"
        leaderboard = "1. Player1: 10 points\n2. Player2: 8 points\n3. Player3: 5 points\n4. Player4: 2 points"

        self.question = question
        self.leaderboard = leaderboard
        self.answer = ""

        # Calculate sizes and positions
        self.board_width = WIDTH - 40
        self.board_height = 200
        self.board_x = 20
        self.board_y = 100

        menu_entry_w = 500

        self.font = FONT


        self.leaderboard_width = 200
        self.leaderboard_height = HEIGHT - 40 - self.board_height
        self.leaderboard_x = WIDTH - self.leaderboard_width - 20
        self.leaderboard_y = self.board_y + self.board_height + 20


        self.input_box_x = 20
        self.input_box_y = HEIGHT - 70

        self.entry_answer = GuiEntry((self.input_box_x, self.input_box_y), self.font, initial_text="", min_w=100,max_length=20, _type=ENTRY_TYPE_NUM)
        self.menu_entry_focus = EntryFocusManager([self.entry_answer])

        submit_button_x = self.input_box_x + 350
        submit_button_y = self.input_box_y

        self.submit_button = GuiButton((submit_button_x, submit_button_y), self.font.render("Submit", True, (0, 0, 0)), min_w=100, callback=self.submit_answer)

        self.time_left = 60
        self.start_time = 0
        self.timer_text = "HAHA"

    def submit_answer(self):
        answer = self.entry_answer.get()
        self.client.send(make_packet(PACKET_GAME_ANSWER, bytes([int(answer)])))

    def server_update(self, packets):
        for packet in packets:
            pID, pDATA = packet
            if pID == PACKET_GAME_WAITING_FOR_NEXT_ROUND:
                self.start_time = 0
                self.timer_text = "WAITING FOR NEW ROUND"
                self.question = ""
            if pID == PACKET_GAME_QUESTION:
                self.start_time = time.time()
                self.question = "Question: " + read_utf8_json(pDATA)[0]


    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.submit_button.update(events,mouse_pos)
        self.menu_entry_focus.update(events,mouse_pos)

        return True

    def draw(self):
        self.screen.fill(WHITE)
        self.entry_answer.draw(self.screen)
        self.submit_button.draw(self.screen)

        # Draw countdown timer
        self.time_left = max(0, 60 - int(time.time() - self.start_time))
        if self.start_time != 0:
            self.timer_text = "Time left: " + str(self.time_left) + " seconds"
        timer_surface = FONT_ACCENT.render(self.timer_text, True, BLACK)
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 40))
        self.screen.blit(timer_surface, timer_rect)

        # Draw question board
        pygame.draw.rect(self.screen, BLACK, (self.board_x, self.board_y, self.board_width, self.board_height), 2)
        text_surface = FONT_ACCENT.render(self.question, True, BLACK)
        self.screen.blit(text_surface, (self.board_x + 10, self.board_y + 10))

        # Draw leaderboard
        pygame.draw.rect(self.screen, BLACK,
                         (self.leaderboard_x, self.leaderboard_y, self.leaderboard_width, self.leaderboard_height), 2)
        font = pygame.font.Font(None, 24)
        leaderboard_lines = self.leaderboard.split('\n')
        for i, line in enumerate(leaderboard_lines):
            text_surface = font.render(line, True, BLACK)
            self.screen.blit(text_surface, (self.leaderboard_x + 10, self.leaderboard_y + 10 + i * 30))

        pygame.display.flip()
# Example usage:
def main():
    pygame.init()
    clock = pygame.time.Clock()

    game_screen = GamePlayScreen(None)
    while True:
        events = pygame.event.get()
        game_screen.handle_events(events )
        game_screen.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

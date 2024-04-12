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

        self.leaderboard = ""
        self.answer = ""

        # Calculate sizes and positions
        self.board_width = WIDTH - 40
        self.board_height = 200
        self.board_x = 20
        self.board_y = 100

        self.question = ""

        menu_entry_w = 500

        self.font = FONT

        self.leaderboard_width = 200
        self.leaderboard_height = HEIGHT - 40 - self.board_height
        self.leaderboard_x = WIDTH - self.leaderboard_width - 20
        self.leaderboard_y = self.board_y + self.board_height + 20

        self.input_box_x = 20
        self.input_box_y = HEIGHT - 70

        self.entry_answer = GuiEntry((self.input_box_x, self.input_box_y), self.font, initial_text="", min_w=100,
                                     max_length=20, _type=ENTRY_TYPE_NUM)
        self.menu_entry_focus = EntryFocusManager([self.entry_answer])

        submit_button_x = self.input_box_x + 350
        submit_button_y = self.input_box_y

        self.submit_button = GuiButton((submit_button_x, submit_button_y), self.font.render("Submit", True, (0, 0, 0)),
                                       min_w=150, callback=self.submit_answer)
        self.point = 1
        self.time_left = 60
        self.start_time = 0
        self.timer_text = "WAITING FOR NEW ROUND"
        self.error_message = ""
        self.submitted = False

    def submit_answer(self):
        if "WAITING" in self.timer_text:
            self.error_message = "Cannot submit answer while waiting for new round."
            return
        if self.submitted:
            self.error_message = "You have already submitted an answer."
            return

        if self.entry_answer.get() == "":
            self.error_message = "Please enter an answer."
            return
            
        self.submitted = True
        self.error_message = ""  # Clear error message
        answer = self.entry_answer.get()
        self.submit_button.content = self.font.render("Submitted", True, (0, 0, 0))
        self.submit_button.disabled = True
        self.client.send(make_packet_string(PACKET_GAME_ANSWER, [answer]))

    def handle_results(self, results):
        print(results)
        leaderboard = []
        for result in results:
            result = result.split(":")

            print(result[0] , result[1])
            if result[0] == self.client.nickname:
                if result[1] == "Disqualified":
                    self.error_message = "You were disqualified."
                    self.client.disconnect()
                    continue
                self.error_message = "You got " + str(int(result[1]) - self.point) + " points for this round."
                leaderboard.append((self.point, result[0]))
                self.point = int(result[1])
            else:
                if result[1] == "Disqualified":
                    leaderboard.append((-2, result[0]))
                elif result[1] == "Disconnected":
                    leaderboard.append((-1, result[0]))
                else:
                    leaderboard.append((int(result[1]), result[0]))
        leaderboard.sort(reverse=True)

        self.leaderboard = ""
        for i, (points, player_id) in enumerate(leaderboard):
            if points == -2:
                self.leaderboard += f"{i + 1}. {player_id}: Disqualified\n"
            elif points == -1:
                self.leaderboard += f"{i + 1}. {player_id}: Disconnected\n"
            else:
                self.leaderboard += f"{i + 1}. {player_id}: {points} points\n"

    def server_update(self, packets):
        for packet in packets:
            pID, pDATA = packet
            if pID == PACKET_GAME_WAITING_FOR_NEXT_ROUND:
                self.start_time = 0
                self.timer_text = "WAITING FOR NEW ROUND"
                self.question = ""
                self.submit_button.content = self.font.render("Submit", True, (0, 0, 0))
                self.submit_button.disabled = False
            if pID == PACKET_GAME_QUESTION:
                self.submitted = False
                self.start_time = time.time()
                self.error_message = ""
                self.question = "Question: " + read_utf8_json(pDATA)[0]
            if pID == PACKET_GAME_LOSE:
                print("LOSE")
            if pID == PACKET_GAME_RESULTS:
                results = read_utf8_json(pDATA)
                self.handle_results(results)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.submit_button.update(events, mouse_pos)
        self.menu_entry_focus.update(events, mouse_pos)

        return True

    def draw(self):
        self.screen.fill(WHITE)
        self.entry_answer.draw(self.screen)
        self.submit_button.draw(self.screen)

        # Draw countdown timer
        self.time_left = max(0, TIME_LIMIT - int(time.time() - self.start_time))
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
                         (self.leaderboard_x, self.leaderboard_y, self.leaderboard_width, self.leaderboard_height),
                         2)
        font = pygame.font.Font(None, 24)
        leaderboard_lines = self.leaderboard.split('\n')
        for i, line in enumerate(leaderboard_lines):
            text_surface = font.render(line, True, BLACK)
            self.screen.blit(text_surface, (self.leaderboard_x + 10, self.leaderboard_y + 10 + i * 30))

        # Draw error message
        if self.error_message:
            error_surface = FONT_LABEL.render(self.error_message, True, RED)
            self.screen.blit(error_surface, (self.board_x + 10, self.board_y + self.board_height + 10))

        pygame.display.flip()


# Example usage:
def main():
    pygame.init()
    clock = pygame.time.Clock()

    game_screen = GamePlayScreen(None, None)
    while True:
        events = pygame.event.get()
        game_screen.handle_events(events)
        game_screen.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()

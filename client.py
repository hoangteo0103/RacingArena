import pygame
import socket
import threading
import time

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
FONT_SIZE = 24
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Player:
    def __init__(self, nickname, position):
        self.nickname = nickname
        self.position = position
        self.points = 0
        self.disqualified = False

    def move(self, steps):
        self.position += steps

class TextInputBox:
    def __init__(self, x, y, width, height, font, color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = ""
        self.font = font
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = BLACK if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.font.size(self.text)[0] + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Render the text.
        text_surface = self.font.render(self.text, True, BLACK)
        # Blit the text.
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the cursor.
        if self.active:
            pygame.draw.rect(screen, BLACK, (self.rect.x + 5 + text_surface.get_width(), self.rect.y + 5, 2, text_surface.get_height()))

class RacingArenaClient:
    def __init__(self, host, port):
        pygame.init()  # Initialize Pygame here
        self.host = host
        self.port = port
        self.nickname_input = TextInputBox(200, 200, 400, 40, pygame.font.Font(None, FONT_SIZE))
        self.nickname = None
        self.player = None
        self.players = []
        self.race_length = 0
        self.start_position = 1
        self.question = None
        self.running = True
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.message = ""
        self.disqualification_message = ""
        self.finished = False
        self.alert_message = ""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Racing Arena")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return False
            self.nickname_input.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.nickname_input.text:
                    self.nickname = self.nickname_input.text
                    self.player = Player(self.nickname, self.start_position)
                    self.send_registration()
                    self.nickname_input.text = ""
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    return False

        return True

    def send_registration(self):
        self.sock.sendall(self.nickname.encode())

    def receive_data(self):
        while self.running:
            try:
                data = self.sock.recv(1024).decode()
                print(data)
                if data.startswith("Registration Completed Successfully"):
                    self.show_waiting_room()
                elif data.startswith("Alert"):
                    self.alert_message = data.split(":")[1]
                elif data.startswith("Race Length"):
                    self.race_length = int(data.split(":")[1])
                elif data.startswith("Start Position"):
                    self.start_position = int(data.split(":")[1])
                elif data.startswith("Question"):
                    self.question = data.split(":")[1]
                elif data.startswith("New round") or data.startswith("Current Race Standings"):
                    self.message = data
                elif data.startswith("Disqualified"):
                    self.disqualification_message = data
                elif data.startswith("Game finished"):
                    self.finished = True
                elif data.startswith("Position"):
                    position = int(data.split(":")[1].split()[0])
                    points = int(data.split(":")[1].split()[1])
                    self.player.points = points
                    self.player.position = position
                elif data.startswith("Remaining players"):
                    self.remaining_players = int(data.split(":")[1])
                    self.update_players(data.split(":")[1])
            except Exception as e:
                print("Error receiving data:", e)
                break

    def update_players(self, player_data):
        player_data = player_data.split("\n")
        self.players = []
        for player_info in player_data:
            if player_info:
                nickname, points = player_info.split(":")
                position, disqualified = points.split()
                self.players.append(Player(nickname.strip(), int(position), int(points.strip()), disqualified.strip() == "True"))

    def draw(self):
        self.screen.fill(WHITE)

        # Display race track
        pygame.draw.line(self.screen, BLACK, (100, 100), (700, 100), 2)
        pygame.draw.line(self.screen, BLACK, (100, 100), (100, 500), 2)
        pygame.draw.line(self.screen, BLACK, (100, 500), (700, 500), 2)
        pygame.draw.line(self.screen, BLACK, (700, 100), (700, 500), 2)

        # Draw players
        for idx, player in enumerate(self.players):
            color = GRAY if player.disqualified else BLACK
            pygame.draw.circle(self.screen, color, (100 + idx * 40, 500 - player.position * 20), 10)
            nickname_text = self.font.render(player.nickname, True, color)
            self.screen.blit(nickname_text, (100 + idx * 40 - 10, 500 - player.position * 20 - 20))

        # Display player's own status
        if self.player:
            pygame.draw.circle(self.screen, BLACK, (100, 550), 10)
            player_text = self.font.render(f"{self.player.nickname}: {self.player.points} points", True, BLACK)
            self.screen.blit(player_text, (120, 540))

        # Display messages
        message_text = self.font.render(self.message, True, BLACK)
        self.screen.blit(message_text, (100, 50))

        if self.disqualification_message:
            disqualification_text = self.font.render(self.disqualification_message, True, BLACK)
            self.screen.blit(disqualification_text, (100, 70))

        # Draw nickname input box
        self.nickname_input.update()
        self.nickname_input.draw(self.screen)

        # Draw alert message
        if self.alert_message:
            alert_font = pygame.font.Font(None, FONT_SIZE)
            alert_text = alert_font.render(self.alert_message, True, RED)
            self.screen.blit(alert_text, (200, 250))

        pygame.display.flip()

    def show_waiting_room(self):
        self.screen.fill(WHITE)
        waiting_font = pygame.font.Font(None, FONT_SIZE)
        waiting_text = waiting_font.render("Waiting for other players...", True, BLACK)
        self.screen.blit(waiting_text, (200, 250))
        pygame.display.flip()

    def send_answer(self, answer):
        self.sock.sendall(answer.encode())

    def run(self):
        clock = pygame.time.Clock()

        while not self.nickname:
            if not self.handle_events():
                return

            self.draw()
            clock.tick(FPS)

        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

        while True:
            if not self.handle_events():
                return

            if self.finished:
                self.running = False

            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345

    client = RacingArenaClient(HOST, PORT)
    client.run()

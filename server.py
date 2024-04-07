import socket
import threading
import random
import time

# Constants
HOST = '127.0.0.1'
PORT = 1234
MAX_PLAYERS = 1  # Example, you can adjust as needed
RACE_LENGTH = 5  # Example, you can adjust as needed
QUESTION_TIME_LIMIT = 10  # Example, you can adjust as needed

class Player:
    def __init__(self, nickname, sock):
        self.nickname = nickname
        self.sock = sock
        self.points = 0
        self.disqualified = False

    def send_message(self, message):
        self.sock.sendall(message.encode())

class RacingArenaServer:
    def __init__(self):
        self.players = []
        self.race_length = RACE_LENGTH
        self.questions = []
        self.current_question = 0
        self.remaining_players = 0
        self.start_position = 1
        self.finished = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.sock.listen(5)
        print(f"Server running on {HOST}:{PORT}")

    def accept_players(self):
        while len(self.players) < MAX_PLAYERS:
            client_sock, client_addr = self.sock.accept()
            nickname = client_sock.recv(1024).decode().strip()
            if self.validate_nickname(nickname):
                player = Player(nickname, client_sock)
                self.players.append(player)
                player.send_message("Registration Completed Successfully\n")
                print(f"Player {nickname} registered.")
            else:
                client_sock.sendall(b"Invalid nickname, please choose another one.\n")
                client_sock.close()

        self.remaining_players = len(self.players)
        self.send_race_info()
        self.generate_questions()

    def validate_nickname(self, nickname):
        if nickname in [player.nickname for player in self.players] or not (0 < len(nickname) <= 10) or not nickname.isalnum():
            return False
        return True

    def send_race_info(self):
        for player in self.players:
            player.send_message(f"Race Length: {self.race_length}\n")
            player.send_message(f"Start Position: {self.start_position}\n")

    def generate_questions(self):
        for _ in range(self.race_length):
            num1 = random.randint(-10000, 10000)
            num2 = random.randint(-10000, 10000)
            operator = random.choice(['+', '-', '*', '/', '%'])
            question = f"{num1} {operator} {num2}"
            self.questions.append(question)

    def play_round(self):
        self.broadcast("New round! Get ready for the next question.\n")
        question = self.questions[self.current_question]
        self.broadcast(f"Question: {question}\n")

        answers = {}
        start_time = time.time()
        for player in self.players:
            player.sock.settimeout(QUESTION_TIME_LIMIT)
            try:
                player.sock.sendall(b"Please submit your answer: ")
                answer = player.sock.recv(1024).decode().strip()
                answers[player.nickname] = answer
            except socket.timeout:
                answers[player.nickname] = None

        end_time = time.time()
        time_taken = end_time - start_time

        correct_answer = eval(question)
        fastest_player = None
        for player in self.players:
            points = 0
            if answers[player.nickname] is None or answers[player.nickname] == "" or not answers[player.nickname].isdigit():
                points = -1
                player.points += points
                if player.points < -2:  # Disqualification condition
                    self.remaining_players -= 1
                    player.disqualified = True
                    self.broadcast(f"{player.nickname} is disqualified!\n")
            elif int(answers[player.nickname]) == correct_answer:
                if fastest_player is None or time_taken < answers[fastest_player]:
                    fastest_player = player.nickname
                points = self.remaining_players if player.nickname == fastest_player else 1
                player.points += points
            else:
                points = -1
                player.points += points
                if player.points < -2:  # Disqualification condition
                    self.remaining_players -= 1
                    player.disqualified = True
                    self.broadcast(f"{player.nickname} is disqualified!\n")

        self.broadcast_results()

        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.finished = True

    def broadcast(self, message):
        for player in self.players:
            player.send_message(message)

    def broadcast_results(self):
        results = "Current Race Standings:\n"
        sorted_players = sorted(self.players, key=lambda x: x.points, reverse=True)
        for i, player in enumerate(sorted_players):
            position = max(self.start_position, i+1)
            results += f"{position}. {player.nickname}: {player.points} points\n"
        self.broadcast(results)

    def run(self):
        accept_thread = threading.Thread(target=self.accept_players)
        accept_thread.start()
        accept_thread.join()

        while not self.finished:
            self.play_round()

        self.broadcast("Game finished.\n")

if __name__ == "__main__":
    server = RacingArenaServer()
    server.run()

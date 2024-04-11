import socket
import threading
import random
import time

class RacingServer:
    def __init__(self, host, port, max_players, race_length, question_time_limit):
        self.host = host
        self.port = port
        self.max_players = max_players
        self.race_length = race_length
        self.question_time_limit = question_time_limit

        self.players = {}  # Dictionary to store players {nickname: (socket, points, disqualified)}
        self.questions = []  # List to store questions
        self.current_question = 0  # Index of the current question
        self.remaining_players = max_players
        self.start_position = 1
        self.finished = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Server running on {self.host}:{self.port}")

    def accept_players(self):
        while len(self.players) < self.max_players:
            client_sock, client_addr = self.sock.accept()
            nickname = client_sock.recv(1024).decode().strip()
            print(nickname , client_addr)
            if self.validate_nickname(nickname):
                self.players[nickname] = (client_sock, 0, False)
                client_sock.sendall(b"Registration Completed Successfully\n")
                print(f"Player {nickname} registered.")
            else:
                print("Duplicated")
                client_sock.sendall(b"Invalid nickname, please choose another one.\n")
                client_sock.close()

            if nickname in self.players:
                del self.players[nickname]
                print(f"Player {nickname} disconnected.")

    def validate_nickname(self, nickname):
        if nickname in self.players.keys() or not (0 < len(nickname) <= 10) or not nickname.isalnum():
            return False
        return True

    def start_game(self):
        print("Starting the game...")
        self.remaining_players = len(self.players)
        self.send_race_info()
        self.generate_questions()
        while not self.finished:
            self.play_round()
        print("Game finished.")

    def send_race_info(self):
        for player in self.players.values():
            player[0].sendall(f"Race Length: {self.race_length}\n".encode())
            player[0].sendall(f"Start Position: {self.start_position}\n".encode())

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
        for nickname, player_info in self.players.items():
            player_sock = player_info[0]
            player_sock.settimeout(self.question_time_limit)
            try:
                player_sock.sendall(b"Please submit your answer: ")
                answer = player_sock.recv(1024).decode().strip()
                answers[nickname] = answer
            except socket.timeout:
                answers[nickname] = None

        end_time = time.time()
        time_taken = end_time - start_time

        correct_answer = eval(question)
        fastest_player = None
        for nickname, answer in answers.items():
            player_info = self.players[nickname]
            player_sock = player_info[0]
            points = 0
            if answer is None or answer == "" or not answer.isdigit():
                points = -1
                player_info = (player_sock, player_info[1] + points, player_info[2])
                self.players[nickname] = player_info
                if player_info[1] < -2:  # Disqualification condition
                    self.remaining_players -= 1
                    player_info = (player_sock, player_info[1], True)
                    self.players[nickname] = player_info
                    self.broadcast(f"{nickname} is disqualified!\n")
            elif int(answer) == correct_answer:
                if fastest_player is None or time_taken < answers[fastest_player]:
                    fastest_player = nickname
                points = self.remaining_players if nickname == fastest_player else 1
                player_info = (player_sock, player_info[1] + points, player_info[2])
                self.players[nickname] = player_info
            else:
                points = -1
                player_info = (player_sock, player_info[1] + points, player_info[2])
                self.players[nickname] = player_info
                if player_info[1] < -2:  # Disqualification condition
                    self.remaining_players -= 1
                    player_info = (player_sock, player_info[1], True)
                    self.players[nickname] = player_info
                    self.broadcast(f"{nickname} is disqualified!\n")

        self.broadcast_results()

        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.finished = True

    def broadcast(self, message):
        for player_info in self.players.values():
            player_info[0].sendall(message.encode())

    def broadcast_results(self):
        results = "Current Race Standings:\n"
        sorted_players = sorted(self.players.items(), key=lambda x: x[1][1], reverse=True)
        for i, (nickname, player_info) in enumerate(sorted_players):
            position = max(self.start_position, i+1)
            results += f"{position}. {nickname}: {player_info[1]} points\n"
        self.broadcast(results)

    def run(self):
        accept_thread = threading.Thread(target=self.accept_players)
        accept_thread.start()
        accept_thread.join()

        self.start_game()


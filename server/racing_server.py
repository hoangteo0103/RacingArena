import socket
import threading
import random
import time
import struct
from server.constant import *

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
        self.sock.settimeout(20)
        self.connected = True

        self.last_ping_sent = 0
        self.last_ping_received = time.time()

        self.buf = b""
        print(f"Server running on {self.host}:{self.port}")

    def read_packets(self, data):
        ## is an index present?
        if len(data) >= 4:
            packet_length = struct.unpack("I", data[:4])[0]

            ## whole packet`1 is present
            if len(data) >= packet_length + 4:
                packet_buf = data[:4 + packet_length]

                ## read the packet: id, payload
                packet = (packet_buf[4], packet_buf[5:])
                print(packet)

            ## move the buffer
            data = data[4 + packet_length:]

            return [packet, *self.read_packets(data)]

        else:
            return []

    def is_socket_connected(self,sock: socket.socket):
        try:
            # Set the socket to non-blocking mode
            sock.setblocking(False)

            # Peek into the socket to check for data
            data = sock.recv(1, socket.MSG_PEEK)

            # If the data is an empty byte string, the socket is not connected
            return False if data == b'' else True
        except BlockingIOError:
            # If the operation will block, set the socket back to blocking mode
            sock.setblocking(True)
            return True
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            # Handle specific connection-related errors
            return False
        finally:
            # Always set the socket back to blocking mode before returning
            sock.setblocking(True)

    def accept_players(self):
        while True:
            client_sock, client_addr = self.sock.accept()
            nickname = client_sock.recv(1024).decode().strip()
            if self.validate_nickname(nickname):
                self.players[nickname] = (client_sock, 0, False)
                client_sock.sendall(b"Registration Completed Successfully\n")
                print(f"Player {nickname} registered.")
            else:
                print("Duplicated")
                client_sock.sendall(b"Invalid nickname, please choose another one.\n")
                client_sock.close()

    def remove_disconnected_players(self):
        while True:
            players_updates = {}
            for player_nickname, (player_socket, _, _) in self.players.items():
                try:
                    data = b"" + player_socket.recv(1024)
                    if data:
                        print("OKEE")
                except socket.error:
                    continue
                except socket.timeout:
                    continue
                packet = list(self.read_packets(data))
                deleted = False
                for p_id, payload in packet:
                    ## received hang
                    if p_id == PACKET_HANG:
                        print("DMDMDMDMDM")
                        player_socket.close()
                        if player_nickname in self.players.keys():
                            try:
                                deleted = True
                            except KeyError:
                                print("ALREADY DELETED")
                        break
                if not deleted:
                    players_updates[player_nickname] = (player_socket, 0, False)
            self.players = players_updates
            time.sleep(1)  # Add a small delay to avoid high CPU usage

    def validate_nickname(self, nickname):
        # Check if nickname is already in use or if it's not alphanumeric or not within length limit
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
        remove_thread = threading.Thread(target=self.remove_disconnected_players)

        accept_thread.start()
        remove_thread.start()

        accept_thread.join()
        remove_thread.join()

        # self.start_game()


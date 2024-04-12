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
        self.sock.listen(TIME_LIMIT)
        self.sock.settimeout(TIME_LIMIT)
        self.connected = True

        self.last_ping_sent = 0
        self.last_ping_received = time.time()
        self.status = STATUS_WAITING_FOR_PLAYERS
        self.buf = b""
        print(f"Server running on {self.host}:{self.port}")

    def read_packets(self, data):
        packets = []

        # Check if an index is present
        if len(data) >= 4:
            packet_length = struct.unpack("I", data[:4])[0]

            # Check if the whole packet is present
            if len(data) >= packet_length + 4:
                packet_buf = data[:4 + packet_length]

                # Read the packet: id, payload
                packet = (packet_buf[4], packet_buf[5:])
                packets.append(packet)

                # Move the buffer
                data =data[4 + packet_length:]

                # Continue reading recursively
                packets.extend(self.read_packets(data))

        return packets

    def is_socket_connected(self,sock: socket.socket):
        try:
            data = b"" + sock.recv(1024)
        except socket.error:
            return False
        except socket.timeout:
            return False

        packet = list(self.read_packets(data))
        for p_id, payload in packet:
            ## received hang
            if p_id == PACKET_HANG:
                sock.close()
                return False
        return True

    def accept_players(self):
        while len(self.players) < self.max_players:
            try:
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                continue
            nickname = client_sock.recv(1024).decode().strip()

            resp = self.validate_nickname(nickname)
            if resp == "":
                self.players[nickname] = (client_sock, 0, False , 0)
                client_sock.sendall(b"Registration Completed Successfully")
                print(f"Player {nickname} registered.")
            else:
                if resp == "DUP":
                    client_sock.sendall(b"Duplicated nickname, please choose another one.")
                if resp == "LEN":
                    client_sock.sendall(b"Nickname length must be shorter than 10, please enter again.")

                client_sock.close()
        time.sleep(WAITING_FOR_INIT)
    def remove_disconnected_players(self):
        while True:
            players_updates = {}
            try:
                for player_nickname, (player_socket, point, status, lose_consecutive) in self.players.items():
                    if self.is_socket_connected(player_socket):
                        players_updates[player_nickname] = (player_socket, 0, False, lose_consecutive)
                    else:
                        players_updates[player_nickname] = (player_socket, 0 , True, lose_consecutive)
                self.players = players_updates
            except RuntimeError:
                continue
    def send_waiting_room_info(self):
        while self.status == STATUS_WAITING_FOR_PLAYERS:
            player_names = []
            for player_nickname, (player_socket, _, status, _) in self.players.items():
                if not status:
                    player_names.append(player_nickname)
            print("SENDING WAITING ROOM INFO", player_names)
            players = self.players
            self.broadcast(make_packet_string(PACKET_PLAYERS_INFO, player_names))
            time.sleep(0.5)
    def validate_nickname(self, nickname):
        if not (0 < len(nickname) <= 10) or not nickname.isalnum():
            return "LEN"
        for player_nickname, (player_socket, _, status, _) in self.players.items():
            if nickname == player_nickname and not status:
                return "DUP"
        return ""

    def start_game(self):
        print("Starting the game...")
        self.status = STATUS_PLAYING
        self.remaining_players = len(self.players)
        self.send_race_info()
        self.generate_questions()
        while not self.finished:
            self.play_round()
        print("Game finished.")

    def send_race_info(self):
        player_names = []
        for player in self.players.values():
            if player[2]:
                player_names.append(player[0])
        self.broadcast(make_packet_string(PACKET_GAME_START, player_names))

    def generate_questions(self):
        for _ in range(self.race_length):
            num1 = random.randint(-10000, 10000)
            num2 = random.randint(-10000, 10000)
            operator = random.choice(['+', '-', '*', '/', '%'])
            question = f"{num1} {operator} {num2}"
            self.questions.append(question)

    def play_round(self):
        self.broadcast(make_packet(PACKET_GAME_WAITING_FOR_NEXT_ROUND, B_EMPTY))

        time.sleep(5)
        self.broadcast(make_packet(PACKET_GAME_NEWROUND, B_EMPTY))
        question = self.questions[self.current_question]
        self.broadcast(make_packet_string(PACKET_GAME_QUESTION, [question]))

        answers = {}
        start_time = time.time()

        # Create a list to store threads
        answer_threads = []

        # Define a function to handle player answer
        def handle_answer(nickname, player_info):
            nonlocal answers
            player_sock = player_info[0]
            player_sock.settimeout(TIME_LIMIT)
            try:
                data = player_sock.recv(1024)
                answer = read_utf8_json(self.read_packets(data))
                print(nickname, answer)
                answers[nickname] = (answer , time.time() - start_time)
            except:
                answers[nickname] = None

        # Create a thread for each player to handle their answer
        for nickname, player_info in self.players.items():
            answer_thread = threading.Thread(target=handle_answer, args=(nickname, player_info))
            answer_thread.start()
            answer_threads.append(answer_thread)

        # Wait for all threads to complete
        for answer_thread in answer_threads:
            answer_thread.join()

        # Find the fastest player and their time taken
        min_time = float('inf')
        for nickname in answers.keys():
            if answers[nickname] is not None and answers[nickname][1] < min_time:
                min_time = answers[nickname][1]

        end_time = time.time()
        time_taken = end_time - start_time
        points = 0
        correct_answer = eval(question)
        fastest_player = None
        for nickname, answer in answers.items():
            player_info = self.players[nickname]
            player_sock = player_info[0]
            if answer is None or answer[0] == "" or not answer.isdigit() or int(answer[0]) != correct_answer:
                points += 1
                player_info = (player_sock, max(1 , player_info[1] -1), player_info[2], player_info[3] + 1)
                self.players[nickname] = player_info
                if player_info[3] == 3 :  # Disqualification condition
                    self.remaining_players -= 1
                    player_info = (player_sock, -1, player_info[2], 0)
                    self.players[nickname] = player_info
            elif int(answer) == correct_answer:
                player_info = (player_sock, player_info[1] + 1, player_info[2], 0)
                self.players[nickname] = player_info

        for nickname in self.players.keys():
            if answers[nickname]  is not None and answers[nickname][1] == min_time:
                self.players[nickname][1] += points

        self.broadcast_results()
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.finished = True

    def broadcast(self, packet):
        for player_info in self.players.values():
            if not player_info[2]:
                player_info[0].sendall(packet)

    def broadcast_results(self):
        result = []
        for nickname, player_info in self.players.items():
            if player_info[2]:
                result.append(nickname + ":" + "Disconnected")
            if player_info[1] == -1:
                result.append(nickname + ":" + "Disqualified")
            if player_info[1] >= 0 and not player_info[2]:
                result.append(nickname + ":" + str(player_info[1]))
        self.broadcast(make_packet_string(PACKET_GAME_RESULTS, result))
    def run(self):
        accept_thread = threading.Thread(target=self.accept_players)
        remove_thread = threading.Thread(target=self.remove_disconnected_players)
        send_waiting_room_info_thread = threading.Thread(target=self.send_waiting_room_info)

        remove_thread.daemon = True
        send_waiting_room_info_thread.daemon = True

        accept_thread.start()
        remove_thread.start()
        send_waiting_room_info_thread.start()

        accept_thread.join()

        self.start_game()


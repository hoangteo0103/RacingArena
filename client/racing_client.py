import socket
import sys
import time

class RacingClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def register(self, nickname):
        self.sock.sendall(nickname.encode())
        print("NOT RESPONDING HERE")
        response = self.sock.recv(1024).decode()
        print(response)
        return response

    def start_race(self):
        try:
            while True:
                message = self.sock.recv(1024).decode()
                print(message)

                if "Race Length" in message:
                    race_length = int(message.split(":")[1])
                    start_position = int(self.sock.recv(1024).decode().split(":")[1])

                    for _ in range(race_length):
                        question = self.sock.recv(1024).decode()
                        print("Question:", question)
                        answer = input("Your answer: ")
                        self.sock.sendall(answer.encode())

                        response = self.sock.recv(1024).decode()
                        print(response)

                    # Receive and print current race standings
                    standings = self.sock.recv(4096).decode()
                    print(standings)

                    # Check if the race is finished
                    race_finished = "Game finished." in standings
                    if race_finished:
                        play_again = input("Race finished. Do you want to play another race? (y/n): ").lower()
                        if play_again != 'y':
                            break
                        else:
                            self.sock.sendall(b"Ready for next race.")
                            continue

        except KeyboardInterrupt:
            print("\nClosing client.")
        finally:
            self.sock.close()

    def disconnect(self):
        print("SOCKET ")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

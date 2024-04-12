import socket
import sys
import time
import struct
from server.constant import *

class RacingClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(5)

        self.last_ping_sent = 0
        self.last_ping_received = time.time()
        self.buf = b""
        self.connected = True

    def read_packets(self):
        packets = []

        # Check if an index is present
        if len(self.buf) >= 4:
            packet_length = struct.unpack("I", self.buf[:4])[0]

            # Check if the whole packet is present
            if len(self.buf) >= packet_length + 4:
                packet_buf = self.buf[:4 + packet_length]

                # Read the packet: id, payload
                packet = (packet_buf[4], packet_buf[5:])
                packets.append(packet)

                # Move the buffer
                self.buf = self.buf[4 + packet_length:]

                # Continue reading recursively
                packets.extend(self.read_packets())

        return packets

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

    def send(self, buf):
        if not self.connected:
            raise Exception("Client not connected!")

        self._send(buf)

        ## for internal use

    def _send(self, buf):
        if not self.connected:
            return

        try:
            self.sock.sendall(buf)
        except:
            self.connected = False

    def ping(self):
        self._send(make_packet(PACKET_PING, B_EMPTY))
        self.last_ping_sent = time.time()

        ## API use

    def disconnect(self):
        if not self.connected:
            return

        self._disconnect()

        ## internal use

    def _disconnect(self):
        if not self.connected:
            return
        print("SOCKET DISCONNECTED")

        ## hack to make sure hang packet gets through
        self.sock.settimeout(20)
        self._send(make_packet(PACKET_HANG, B_EMPTY))
        self.connected = False

        ## update, handles internal stuff and is for API use

    def update(self):
        if not self.connected:
            return None

        try:
            data = self.sock.recv(1024)
            if data:
                self.buf += data

        except socket.error:
            pass

        ## some internal packets get handled internally
        ## all get returned
        packets = list(self.read_packets())

        ## internal handling
        ## sending ping

        self.ping()

        ## iterate packets (only internal packets are handled)
        for p_id, payload in packets:

            ## received ping
            if p_id == PACKET_PING:
                ##print(self._kind, "ping received", self.last_ping_received)
                self.last_ping_received = time.time()

            ## received hang
            if p_id == PACKET_HANG:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.connected = False
                return

        return packets

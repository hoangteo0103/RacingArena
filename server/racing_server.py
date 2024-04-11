from server.networking import *
from server.constant import *
import datetime

class RacingServer:
    def __init__(self, ip, port):
        print(ip, port)
        self.server = Server((ip, port))
        self.status = STATUS_WAITING_FOR_PLAYERS

    def broadcast(self, buf):
        self.server.broadcast(buf)

    def change_status(self, status):
        self.status = status
        self.broadcast_status()

    def broadcast_status(self):
        print("broadcasting status:", self.status)
        self.broadcast(make_packet(PACKET_STATUS, bytes([self.status])))

    def broadcast_board(self, is_capture=0):
        pass


    def broadcast_client_info(self):
        for idx, client in self.server.get_clients():
            for idx2, update_client in self.server.get_clients():
                update_client.send(make_packet(PACKET_PLAYER_INFO, bytes([idx]) + write_utf8_string(client.nick)))
    def update(self):
        if self.status == STATUS_SERVER_STOPPED:
            return

        ## send status packet to new clients
        if len(self.server.get_new_clients()) > 0:
            self.broadcast_status()

        if self.status == STATUS_PLAYING and self.server.get_num_clients() <= 1:
            self.change_status(STATUS_GAME_ENDED_PLAYER_LEFT)

        ## enough clients
        if self.status == STATUS_WAITING_FOR_PLAYERS and self.server.get_num_clients() == 2:
            self.change_status(STATUS_PLAYING)
            self.broadcast_board()

            self.server.get_client(0).send(make_packet(PACKET_SIDE, bytes([0])))
            self.server.get_client(1).send(make_packet(PACKET_SIDE, bytes([1])))

            self.start_time = datetime.now()

    def stop(self):
        self.status = STATUS_SERVER_STOPPED
        self.server.stop()

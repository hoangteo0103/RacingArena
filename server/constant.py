import struct

UTIL_STATUS_HUMAN_READABLE = ["Waiting for opponent!", "Game", "Game ended!", "Opponent left!", "Server shutting down!", "Connection lost!"]

def write_utf8_string(string):
    buf = string.encode("utf-8")

    return struct.pack("I", len(buf)) + buf

def read_utf8_string(buf):
    l = struct.unpack("I", buf[0:4])[0]

    return buf[4:4+l].decode("utf-8")

def make_packet(_id, payload):
    b = bytes([_id]) + payload

    return struct.pack("I", len(b)) + b
## Server status
STATUS_NOT_CONNECTED = -1 ## only for client
STATUS_WAITING_FOR_PLAYERS = 0
STATUS_PLAYING = 1
STATUS_GAME_ENDED = 2
STATUS_GAME_ENDED_PLAYER_LEFT = 3
STATUS_SERVER_STOPPED = 4

## Packet
B_EMPTY = b""
PACKET_PING = 0
PACKET_HANG = 1
PACKET_STATUS = 2               ## int8 status
PACKET_SET_NICK = 3             ## utf8_string nick
PACKET_PLAYER_INFO = 4          ## int8 idx, utf8_string nick
PACKET_SIDE = 5                 ## int8 side
PACKET_BOARD = 6                ## int8 is_capture utf8_string board_epd
PACKET_GIVE_UP = 7              ## give up
PACKET_MOVE = 8                 ## int8 from, int8 to
PACKET_GAME_OUTCOME = 9         ## int8 termination, int8 winner
PACKET_CLIENT_MOVE_INFO = 10    ## int8 from, int8 to               info for client to see what was moved
PACKET_CLIENT_TAKEN_INFO = 11   ## int8 piece                       info for client to see what was taken
PACKET_GAME_START = 12

OUTCOME_RESIGNED = 11




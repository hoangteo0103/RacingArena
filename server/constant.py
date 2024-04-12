import struct
import json

UTIL_STATUS_HUMAN_READABLE = ["Waiting for opponent!", "Game", "Game ended!", "Opponent left!", "Server shutting down!", "Connection lost!"]

def make_packet_string(_id, payload):
    payload_json = json.dumps(payload)  # Convert the payload list to a JSON string
    payload_bytes = payload_json.encode('utf-8')  # Encode the JSON string to bytes

    b = bytes([_id]) + payload_bytes

    return struct.pack("I", len(b)) + b

def read_utf8_json(buf):
    payload_json = buf.decode('utf-8')

    # Decode the JSON string back to a list
    payload_list = json.loads(payload_json)
    return payload_list
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
PACKET_STATUS = 2
PACKET_SET_NICK = 3
PACKET_PLAYERS_INFO = 4
PACKET_GAME_START = 5
PACKET_GAME_NEWROUND = 6
PACKET_GAME_ANSWER = 7
PACKET_GAME_QUESTION = 8
PACKET_GAME_WAITING_FOR_NEXT_ROUND = 9
PACKET_GAME_WRONG_ANSWER = 10
PACKET_GAME_CORRECT_ANSWER = 11
PACKET_GAME_LOSE = 12

OUTCOME_RESIGNED = 8

## GAME CONFIG

MAX_PLAYERS = 1
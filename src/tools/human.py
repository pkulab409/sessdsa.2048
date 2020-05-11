# 人机对战用的伪ai, 需要注意设置超时时间

import webbrowser, os, json, sys
import socket
import struct
import hashlib
import base64

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE_CONN = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA


class WSS:
    @classmethod
    def make_handshake_response(cls, key, host):
        return \
            'HTTP/1.1 101 Switching Protocols\r\n'  \
            'Upgrade: websocket\r\n'                \
            'Connection: Upgrade\r\n'               \
            'Sec-WebSocket-Accept: {}\r\n'          \
            'WebSocket-Location: ws://{}\r\n'       \
            '\r\n'.format(cls.calculate_response_key(key), host)

    @classmethod
    def calculate_response_key(cls, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = hashlib.sha1(key.encode() + GUID.encode())
        response_key = base64.b64encode(hash.digest()).strip()
        return response_key.decode('ASCII')

    def read_http_headers(self):
        headers = {}
        # first line should be HTTP GET
        http_get = self.rfile.readline().decode().strip()
        assert http_get.upper().startswith('GET')
        # remaining should be headers
        while True:
            header = self.rfile.readline().decode().strip()
            if not header:
                break
            head, value = header.split(':', 1)
            headers[head.lower().strip()] = value.strip()
        return headers

    def read_bytes(self, num):
        # python3 gives ordinal of byte directly
        data = self.rfile.read(num)
        if sys.version_info[0] < 3:
            return map(ord, data)
        else:
            return data

    def __init__(self, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", port))
        self.socket.listen(1)
        self.keep_alive = True
        self.handshake_done = False

    def wait_for_connection_and_do_handshake(self):
        self.connection, self.addr = self.socket.accept()
        print(self.addr)
        self.rfile = self.connection.makefile("rb")
        self.wfile = self.connection.makefile("wb")
        headers = self.read_http_headers()
        print(headers)
        assert 'upgrade' in headers
        assert headers['upgrade'].lower() == 'websocket'
        assert 'sec-websocket-key' in headers
        key = headers['sec-websocket-key']
        response = self.make_handshake_response(key, headers.get("host"))
        self.connection.sendall(response.encode())
        self.handshake_done = True

    def send_bytes(self, payload, opcode=OPCODE_TEXT):
        assert isinstance(payload, bytes)
        header = bytearray()
        payload_length = len(payload)
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(payload_length)
        # Extended payload
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))
        # Huge extended payload
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))
        else:
            raise Exception("Message is too big")
        self.connection.sendall(header + payload)

    def send(self, message):
        try:
            self.send_bytes(str(message).encode())
        except:
            self.connection.close()
            self.connection = None

    def read_next_message(self) -> str:
        b1, b2 = self.read_bytes(2)
        fin = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            raise Exception("Client asked to close connection.")
        if not masked:
            raise Exception("Client must always be masked.")
        if opcode == OPCODE_CONTINUATION:
            raise Exception("Continuation frames are not supported.")
        elif opcode == OPCODE_BINARY:
            raise Exception("Binary frames are not supported.")
        elif not opcode in [OPCODE_TEXT, OPCODE_PING, OPCODE_PONG]:
            raise Exception("Unknown opcode %#x." % opcode)

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.rfile.read(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.rfile.read(8))[0]

        masks = self.read_bytes(4)
        message_bytes = bytearray()
        for message_byte in self.read_bytes(payload_length):
            message_byte ^= masks[len(message_bytes) % 4]
            message_bytes.append(message_byte)

        if opcode != OPCODE_TEXT:
            if opcode == OPCODE_PONG:
                pass
            if opcode == OPCODE_PING:
                self.send_bytes(message_bytes, opcode=OPCODE_PONG)
            return self.read_next_message()

        return message_bytes.decode('utf8')

    def recv(self) -> str:
        try:
            return self.read_next_message()
        except:
            self.connection.close()
            self.connection = None
            return ""

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
        try:
            self.socket.close()
        except:
            pass


class PlayerServer:
    def __init__(self) -> None:
        path_split = "/"
        if os.name == "nt":
            path_split = "\\"
        directory, _ = os.path.split(os.path.realpath(__file__))
        self.WSServer = WSS(9001)
        print(directory + path_split + "human.html")
        print(webbrowser.open_new_tab(directory + path_split + "human.html"))

    def send(self, message):
        self.WSServer.send(message)

    def recv(self) -> str:
        return self.WSServer.recv()

    def __del__(self):
        print("del ps")


class Player:
    ps = PlayerServer()

    def __init__(self, isFirst, array):
        self.isFirst = isFirst
        self.array = array

        try:
            Player.ps.WSServer.connection.close()
        except:
            pass
        while not Player.ps.WSServer.handshake_done:
            Player.ps.WSServer.wait_for_connection_and_do_handshake()
        Player.ps.send(json.dumps({"is_first": isFirst}))

    def output(self, currentRound, board, mode):
        if mode == 'position':  # 给出己方下棋的位置
            another = board.getNext(self.isFirst, currentRound)  # 己方的允许落子点
            self.ps.send(
                json.dumps({
                    "current_round": currentRound,
                    "board": repr(board),
                    "mode": mode,
                    "available": list(another)
                }))
            recv = Player.ps.recv()
            recv = json.loads(recv)
            print(recv)
            return tuple(recv["action"])
        else:  # 给出己方合并的方向
            self.ps.send(
                json.dumps({
                    "current_round": currentRound,
                    "board": repr(board),
                    "mode": mode,
                    "available": list()
                }))
            recv = Player.ps.recv()
            recv = json.loads(recv)
            print(recv)
            return recv["action"]


if __name__ == "__main__":
    ws = Player.ps.WSServer
    ws.send_bytes(b"test" * 128)
    ws.send("test" * 128)
    while True:
        recv = ws.recv()
        print(recv)
        ws.send(recv)

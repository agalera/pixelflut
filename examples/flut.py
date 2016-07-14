import multiprocessing
from websocket import create_connection
import json
import time

queue = multiprocessing.Queue()


def rshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def draw(initx, inity, finx, finy):
    ws = create_connection("ws://localhost:1234/ws")
    for y in range(inity, finy):
        for x in range(initx, finx):
            _time = int(time.time() * 10000)
            r = (rshift(_time, 4)) % 255
            g = (rshift(_time, 8)) % 255
            b = (rshift(_time, 12)) % 255
            ws.send(json.dumps([x, y, r, g, b, 255]))

t = multiprocessing.Process(target=draw, args=(0, 0, 320, 240))
t.start()
t = multiprocessing.Process(target=draw, args=(320, 0, 640, 240))
t.start()
t = multiprocessing.Process(target=draw, args=(0, 240, 320, 480))
t.start()
t = multiprocessing.Process(target=draw, args=(320, 240, 640, 480))
t.start()

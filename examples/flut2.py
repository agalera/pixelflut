import random
from websocket import create_connection
import json
from PIL import Image

w = 640
h = 480
matrix = [[None for y in range(h)] for x in range(w)]

clients = []
im = Image.open("MER_640_480.jpg")
pix = im.load()

ws = create_connection("ws://localhost:1234/ws")
matrix = []
for x in range(w):
    for y in range(h):
        matrix.append((x, y))

random.shuffle(matrix)

for x, y in matrix:
    r, g, b = pix[x, y]
    ws.send(json.dumps([x, y, r, g, b, 255]))

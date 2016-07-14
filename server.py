import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.escape
import json


w = 640
h = 480
matrix = [[[200, 200, 200, 255] for y in range(h)] for x in range(w)]

clients = []


class Index(tornado.web.RequestHandler):
    def get(self):
        response = """
            <canvas id="draw" width="640", height="480"></canvas>
            <script>
            var canvas = document.getElementById("draw");
            var canvasWidth = canvas.width;
            var canvasHeight = canvas.height;
            var ctx = canvas.getContext("2d");
            var canvasData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);

            // That's how you define the value of a pixel //
            function drawPixel (x, y, r, g, b, a) {
                var index = (x + y * canvasWidth) * 4;

                oldr = canvasData.data[index + 0]
                oldg = canvasData.data[index + 1]
                oldb = canvasData.data[index + 2]
                alpha = a / 255
                canvasData.data[index + 0] = alpha * r + (1 - alpha) * oldr;
                canvasData.data[index + 1] = alpha * g + (1 - alpha) * oldg;
                canvasData.data[index + 2] = alpha * b + (1 - alpha) * oldb;
                canvasData.data[index + 3] = 255;
            }

            // That's how you update the canvas, so that your //
            // modification are taken in consideration //
            function updateCanvas() {
                ctx.putImageData(canvasData, 0, 0);
            }
            var connection = new WebSocket('ws://'+location.hostname+':1234/ws');

            connection.onclose = function () {
                // connection is opened and ready to use
                   console.log("close");
            };

            connection.onopen = function () {
                // connection is opened and ready to use
                   connection.send("web");
            };

            connection.onerror = function (error) {
                // an error occurred when sending/receiving data
                    console.log(error);
            };

            connection.onmessage = function (message) {
                r = JSON.parse(message.data);
                drawPixel(r[0], r[1], r[2], r[3], r[4], r[5]);
            };
            function refresh_image(matrix) {
                matrix = matrix.matrix;
                for (x = 0; x < matrix.length; x++) {
                    for (y = 0; y < matrix[x].length; y++) {
                        values = matrix[x][y];
                        drawPixel(x, y, values[0], values[1], values[2], values[3]);
                    }
                }
                updateCanvas();
            }
            var getJSON = function(url, callback) {
                var xhr = new XMLHttpRequest();
                xhr.open("get", url, true);
                xhr.responseType = "json";
                xhr.onload = function() {
                  var status = xhr.status;
                  if (status == 200) {
                    callback(xhr.response);
                  }
                };
                xhr.send();
            };
            window.setInterval(function(){
                updateCanvas();
            }, 100);
            getJSON("http://"+location.hostname+":1234/info", refresh_image);
            </script>
        """
        self.write(response)


class Info(tornado.web.RequestHandler):
    def post(self):
        send_message(self.request.body)

    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(tornado.escape.json_encode({'matrix': matrix}))


def send_message(message):
    message = message
    delete = []
    for client in clients:
        try:
            client.write_message(message)
        except:
            delete.append(client)

    for x in delete:
        print("remove client")
        clients.remove(x)


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        if message == "web":
            clients.append(self)
            return
        m = json.loads(message)
        x, y = m[0], m[1]
        alpha = m[5] / 255.0
        r = int(alpha * m[2] + (1 - alpha) * matrix[x][y][0])
        g = int(alpha * m[3] + (1 - alpha) * matrix[x][y][1])
        b = int(alpha * m[4] + (1 - alpha) * matrix[x][y][2])
        matrix[x][y] = [r, g, b, 255]

        send_message(message)

    def on_close(self):
        pass

    def check_origin(self, origin):
        return True

application = tornado.web.Application([
    (r'/', Index),
    (r'/info', Info),
    (r'/ws', WSHandler),
])


def main():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(1234)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

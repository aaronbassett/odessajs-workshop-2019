import tornado.websocket
from logzero import logfile, logger

logfile("/tmp/odessajs-workshop.log", maxBytes=1e6, backupCount=3)


class WebSocketClientCounter(tornado.websocket.WebSocketHandler):

    connected_clients = []

    def check_origin(self, origin):
        return True

    def open(self):
        WebSocketClientCounter.connected_clients.append(self)
        logger.info(f"Client connected [{len(self.connected_clients)}]")

    def on_close(self):
        WebSocketClientCounter.connected_clients.remove(self)
        logger.warn(f"Client disconnected [{len(self.connected_clients)}]")


if __name__ == "__main__":
    app = tornado.web.Application(
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
            (r"/", WebSocketClientCounter),
        ],
        debug=True,
        autoreload=True,
    )
    app.listen(8000)

    logger.debug("Starting WebSocket server")
    tornado.ioloop.IOLoop.current().start()

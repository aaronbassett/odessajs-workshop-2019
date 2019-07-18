import json
import signal
import tornado.websocket
from tornado import gen
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import StreamClosedError
import arrow
from logzero import logfile, logger

logfile("/tmp/odessajs-workshop.log", maxBytes=1e6, backupCount=3)


class ClientWithout(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/without.html")


class ClientWithoutWidget(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/without-widget.html")


class ClientWith(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/with.html")


class ClientWithWidget(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/with-widget.html")


class WebSocketClientCounter(tornado.websocket.WebSocketHandler):

    connected_clients = []

    def check_origin(self, origin):
        return True

    def open(self):
        WebSocketClientCounter.connected_clients.append(self)
        self.update_clients()
        logger.info(f"Client connected [{len(self.connected_clients)}]")

    def on_close(self):
        WebSocketClientCounter.connected_clients.remove(self)
        self.update_clients()
        logger.warning(f"Client disconnected [{len(self.connected_clients)}]")

    def on_message(self, message):
        self.update_clients()

    def update_clients(self):
        utc = arrow.utcnow()
        for connected_client in self.connected_clients:
            connected_client.write_message(
                json.dumps(
                    {
                        "connections": len(self.connected_clients),
                        "updated": utc.humanize(),
                    }
                )
            )


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = (b, a + b) if a < 1000 else (0, 1)


class DataSource(object):
    def __init__(self, initial_data=None):
        self._data = initial_data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data


class EventSource(tornado.web.RequestHandler):
    def initialize(self, source):
        self.source = source
        self._last = None
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')

    @gen.coroutine
    def publish(self, data):
        try:
            self.write(f"data: {data}\n\n")
            yield self.flush()
        except StreamClosedError:
            pass

    @gen.coroutine
    def get(self):
        while True:
            if self.source.data != self._last:
                yield self.publish(self.source.data)
                self._last = self.source.data
            else:
                yield gen.sleep(0.005)


class SSEWithout(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/sse-without.html")


class SSEWithoutWidget(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/sse-without-widget.html")

if __name__ == "__main__":

    generator = fibonacci()
    publisher = DataSource(next(generator))

    def get_next():
        publisher.data = next(generator)

    checker = PeriodicCallback(lambda: get_next(), 3000.0)
    checker.start()

    app = tornado.web.Application(
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
            (r"/", WebSocketClientCounter),
            (r"/without", ClientWithout),
            (r"/without-widget", ClientWithoutWidget),
            (r"/with", ClientWith),
            (r"/with-widget", ClientWithWidget),
            (r'/sse', EventSource, dict(source=publisher)),
            (r"/sse-without", SSEWithout),
            (r"/sse-without-widget", SSEWithoutWidget),
        ],
        debug=True,
        autoreload=True,
    )
    app.listen(8000)

    logger.debug("Starting WebSocket server")
    signal.signal(signal.SIGINT, lambda x, y: IOLoop.instance().stop())
    IOLoop.instance().start()

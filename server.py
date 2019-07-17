import tornado.websocket
from logzero import logfile, logger

logfile("/tmp/odessajs-workshop.log", maxBytes=1e6, backupCount=3)


if __name__ == "__main__":
    app = tornado.web.Application(
        [(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"})],
        debug=True,
        autoreload=True,
    )
    app.listen(8000)

    logger.debug("Starting WebSocket server")
    tornado.ioloop.IOLoop.current().start()

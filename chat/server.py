from os import path as op

import tornado.web
import tornadio2
import tornadio2.router
import tornadio2.server
import tornadio2.conn

ROOT = op.normpath(op.dirname(__file__))   #获取基础地址，如果不写就是当前地址
#以下的方法都是标准的接口架构，往里面填代码就行

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')


class SocketIOHandler(tornado.web.RequestHandler): #这个js库在上层
    def get(self):
        self.render('../socket.io.js')


class WebSocketFileHandler(tornado.web.RequestHandler):
    def get(self):
        # Obviously, you want this on CDN, but for sake of
        # example this approach will work.
        self.set_header('Content-Type', 'application/x-shockwave-flash')

        with open(op.join(ROOT, '../WebSocketMain.swf'), 'rb') as f:
            self.write(f.read())
            self.finish()


class ChatConnection(tornadio2.conn.SocketConnection):
    # Class level variable
    participants = set()

    def on_open(self, info):                    #当网页发起连接后发送
        self.send("Welcome from the server.")
        self.participants.add(self)             #保存客户端客户的信息

    def on_message(self, message):              #有消息进来后
        # Pong message back
        for p in self.participants:             #进行广播
            p.send(message)

    def on_close(self):                         #连接关闭后删除信息
        self.participants.remove(self)

# Create chat server
ChatRouter = tornadio2.router.TornadioRouter(ChatConnection, dict(websocket_check=True))

# Create application
application = tornado.web.Application(
    ChatRouter.apply_routes([(r"/", IndexHandler),
                             (r"/socket.io.js", SocketIOHandler),
                             (r"/WebSocketMain.swf", WebSocketFileHandler)
                            ]),
    flash_policy_port = 843,
    flash_policy_file = op.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8001
)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    tornadio2.server.SocketServer(application)




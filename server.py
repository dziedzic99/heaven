import http.server
import socketserver
import logging

PORT = 8002


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        logging.info("GET request", self.headers)
        super(ServerHandler, self).do_GET()

    def do_POST(self):
        logging.info("POST request", self.headers)
        super(ServerHandler, self).do_POST()


httpd = socketserver.TCPServer(("", PORT), ServerHandler)

print("serving at port", PORT)
httpd.serve_forever()

from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import urllib.parse
import mimetypes
import pathlib
import socket
import json

BASE_DIR = pathlib.Path()


def send_data_to_socket(body):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(body, ('127.0.0.1', 5000))
    client_socket.close()


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(200)
        self.send_header('Content-type', 'text.html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run_server(server=HTTPServer, handler=HTTPHandler):
    address = ('', 3000)
    http_server = server(address, handler)
    http_server.serve_forever()


def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as file:
            json.dump(data_dict, file, ensure_ascii=False)
    except ValueError:
        print("Error, not correct message. Please don't use '= and &'")

        
def run_socket_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock = ip, port
        server.bind(sock)
        while True:
            data = server.recv(1024)
            if not data:
                break
            save_data(data)


if __name__ == '__main__':
    thread_server = Thread(target=run_server)
    thread_server.start()

    thread_socket = Thread(target=run_socket_server('127.0.0.1', 5000))
    thread_socket.start()
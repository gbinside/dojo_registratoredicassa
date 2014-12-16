#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import Tk, BOTH, Frame
from Queue import Queue, Empty
from threading import Thread
import BaseHTTPServer
import Tkinter as tk
import json
try:
    import winsound
except ImportError:
    pass

TIMEOUT = 1
HOST = '127.0.0.1'
PORT = 5000

ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"

queue = Queue()


class HandlerClass(BaseHTTPServer.BaseHTTPRequestHandler):
    app = None

    def do_POST(s):
        if s.path == '/':
            try:
                content_lenght = int(s.headers['Content-Length'])
                post_data = json.loads(s.rfile.read(content_lenght))
                HandlerClass.app.display(post_data['display'])
            except:
                s.send_response(500)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write(json.dumps({'status': 'KO'}))

            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps({'status': 'OK'}))
        else:
            s.send_response(404)


    def do_GET(s):
        if s.path == '/':
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            try:
                barcode = queue.get(timeout=TIMEOUT)
                s.wfile.write(json.dumps({'status': 'OK', 'barcode': barcode}))
                queue.task_done()
            except Empty:
                s.wfile.write(json.dumps({'status': 'Empty'}))
        else:
            s.send_response(404)


class WebserverThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.server_address = (HOST, PORT)
        HandlerClass.protocol_version = Protocol
        HandlerClass.app = app
        self.httpd = ServerClass(self.server_address, HandlerClass)

    def run(self):
        sa = self.httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        self.httpd.serve_forever()


def beep():
    try:
        winsound.Beep(1000, 300)
    except NameError:
        print chr(7)


class Cassa(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self._barcode_label = tk.Label(self, text='Barcode')
        self._enqueue_button = tk.Button(self, text='Scan', command=self.enqueue)
        self._display = tk.Text(self, wrap=tk.NONE, height=1)
        self._barcode = tk.Text(self, wrap=tk.NONE, height=1)
        self.parent = parent

        self.init_ui()

    def enqueue(self):
        beep()
        queue.put(self._barcode.get(1.0, tk.END).strip(' \t\n'))

    def display(self, s):
        self._display.config(state=tk.NORMAL)
        self._display.delete("1.0", tk.END)
        self._display.insert(tk.INSERT, s, 'right')
        self._display.config(state=tk.DISABLED)

    def init_ui(self):
        self.parent.title("Registratore di Cassa")
        self.pack(fill=BOTH, expand=1)

        self._display.pack(fill=tk.X, expand=1)
        self._display.tag_config('right', justify=tk.RIGHT)
        self._display.insert(tk.INSERT, '0,00', 'right')
        self._display.config(state=tk.DISABLED)

        self._barcode_label.pack(fill=tk.X)
        self._barcode.pack(fill=tk.X, expand=1)
        self._enqueue_button.pack(fill=tk.X, expand=1)


def main():
    root = Tk()
    root.geometry("300x100+300+300")
    app = Cassa(root)

    c = WebserverThread(app)
    c.daemon = True
    c.start()

    root.mainloop()


if __name__ == '__main__':
    main()

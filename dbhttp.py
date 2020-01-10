# -*- coding: utf-8 -*-
import os, http, threading, json, traceback
import dbagent
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """
    
_dbclient = None 

'''
reference: https://zhuanlan.zhihu.com/p/32136384
'''
class DBHttpServerHandler(SimpleHTTPRequestHandler):
            
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        # override the parent log message to avoid output useless log
        pass
    
    def do_GET(self):
        self._set_headers()
        self.wfile.write(("Please use post").encode())

    def do_POST(self):
        self._set_headers()
        try:
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string.decode('UTF-8'))
            _dbclient.insertData(data["table"], data["data"])
        except Exception:
            self.wfile.write(b"FAILED")
            traceback.print_exc()
        else:
            self.wfile.write(b"OK")

def startHttpServer(port, db):
    global _dbclient
    _dbclient = db
    
    def thread_func(port):
        httpd = ThreadedHTTPServer(('', port), DBHttpServerHandler)
        print('Starting db httpd on ' + str(port) + '...')
        httpd.serve_forever()
      
    threading.Thread(target=thread_func, args=(port,)).start()        
    
if __name__ == "__main__":
    startHttpServer(8090, dbagent.DBAgent())
    #startHttpServer(8090, None)
    while True:
        pass
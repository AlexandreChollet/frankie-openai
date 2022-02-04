#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

from http.server import HTTPServer, BaseHTTPRequestHandler
import openai
import cgi
import json
import atexit
import unicodedata
import sys
import os
import re
from functools import partial
from dotenv import load_dotenv
from importlib import reload

class handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/message/process':
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            json_body = json.loads(post_body)
            message = json_body['content']

            print('Received : ' + message)

            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
            # acceptation de json seulement
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return

            # traitement avec pyborg
            completion = openai.Completion.create(engine="text-davinci-001", prompt=message, temperature=0.5, max_tokens=240, frequency_penalty=1.75)
            print('Sending : ' + completion.choices[0].text)

            self._set_headers()
            self.wfile.write(json.dumps({'reply': completion.choices[0].text}).encode())
            
        else:
           self.error()

    def error(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def sendInput(self, message):
        print('processing ' + message.decode('utf-8') + '...')
        result = handler.pyborg_interface.process_msg(self, message, 100, 1, 'tort', 1)
        if(result is not None):
            print('replied with : "' + result.decode('utf-8') + '"')
        else:
            print('No reply given.')
        return result

    def output(self, reply, args):
        pass

def main():
    reload(sys)
    load_dotenv()
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    PORT = 4000
    server = HTTPServer(('', PORT), handler)
    print('Server running on port %s' % PORT)
    server.serve_forever()

if __name__ == '__main__':
    main()
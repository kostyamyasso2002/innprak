#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
import cgi
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import speech_recogniser


def process_file(audio_file: str) -> dict:
    transcript = speech_recogniser.transcript_audio(audio_file)
    try:
        left = speech_recogniser.get_left_fragments(transcript["result"])
    except KeyError:
        left = []
    ans = {"left_fragments": []}
    for frag in left:
        ans["left_fragments"].append({"start": frag[0], "end": frag[1]})

    return ans


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(str.encode(json.dumps({'hello': 'world', 'received': 'ok'})))

    # POST echoes the message adding a JSON field
    # def do_POST1(self):
    #     ctype, pdict = cgi.parse_header(self.headers['content-type'])
    #
    #     # refuse to receive non-json content
    #     if ctype != 'application/json':
    #         self.send_response(400)
    #         self.end_headers()
    #         return
    #
    #     # read the message and convert it into a python dictionary
    #     length = int(self.headers['content-length'])
    #     message = json.loads(self.rfile.read(length))
    #
    #     # add a property to the object, just to mess with data
    #     message['received'] = 'ok'
    #
    #     # send the message back
    #     self._set_headers()
    #     print(message)
    #     self.wfile.write(str.encode(json.dumps(message)))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        # refuse to receive non-json content
        if ctype != 'application/octet-stream':
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers['content-length'])
        audio = self.rfile.read(length)

        print(type(audio))

        tmp_file = open("tmp.wav", "wb")
        tmp_file.write(audio)

        self._set_headers()
        self.wfile.write(str.encode(json.dumps(process_file("tmp.wav"))))


def run(server_class=HTTPServer, handler_class=Server, port=6593):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

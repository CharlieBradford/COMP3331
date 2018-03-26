from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
httpd = HTTPServer(('', int(sys.argv[1])), SimpleHTTPRequestHandler)
httpd.serve_forever()

import http.server
import socketserver
import time

PORT = 8004
DIRECTORY = "app"
DEFAULT_PAGE = "app.html"


class CustomHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # print(f"GET: {self.path=}")
        if self.path == "/":
            self.path = DEFAULT_PAGE
        if "/?" in self.path:
            self.path = self.path.replace("/?", f"/{DEFAULT_PAGE}?")
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


with socketserver.TCPServer(("", PORT), CustomHttpRequestHandler) as httpd:
    print(f"Custom http.server on port {PORT} from dir {DIRECTORY} with default page {DEFAULT_PAGE}. "
                f"Press CTRL+C to close the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        httpd.server_close()
        time.sleep(1)
        print(f"Server on port {PORT} closed.")

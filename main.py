from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.parse
import webbrowser
import mimetypes
import json

from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path(__file__).parent
jinja = Environment(loader=FileSystemLoader("templates"))


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.render_tamplate("read.jinja")
        else:
            file = BASE_DIR.joinpath(pr_url.path[1:])
            if file.exists():
                self.send_static(file)
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value
            for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        from datetime import datetime
        timestamp = datetime.now().isoformat()
        data_file = BASE_DIR / "storage/data.json"

        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = {}
        else:
            messages = {}

        messages[timestamp] = data_dict

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        print(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def render_tamplate(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("storage/data.json", "r", encoding="utf-8") as fd:
            data = json.load(fd)

        template = jinja.get_template(filename)
        content = template.render(messages=data)
        self.wfile.write(content.encode())

    def send_static(self, filename, status=200):
        self.send_response(status)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-type", mime_type)
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)

    print("Server is running on http://localhost:3000")
    webbrowser.open("http://localhost:3000")

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        print("\nServer stopped.")


if __name__ == "__main__":
    run()

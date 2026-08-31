import socket

with socket.socket() as server:
    server.bind(("0.0.0.0", 8888))
    server.listen(1)

    print("8888 포트에서 요청 대기 중...")

    client, address = server.accept()

    with client:
        log = client.recv(8192).decode(errors="replace")

        client.sendall(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Length: 2\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"OK"
        )
    with open("request.log", "a", encoding="utf-8") as file:
        file.write(log)
        
print("수신 완료")

'''
New-NetFirewallRule `
  -DisplayName "Python Receiver 8888" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8888 `
  -Action Allow
'''

'''
Remove-NetFirewallRule -DisplayName "Python Receiver 8888"
'''
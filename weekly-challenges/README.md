# Weekly Challenges

`weekly-challenges/`에는 T34M ROOKIE 스터디에서 사용하는 주차별 공통 CTF 문제를 보관합니다.

대부분 기존 CTF의 공개 소스 또는 `sajjadium/ctf-archives`에 보존된 문제를 기반으로 하며, 로컬 스터디 환경에서 재현할 수 있도록 Docker 실행 환경, 포트, 플래그 처리 등을 조정했습니다.

> 원본 문제의 저작권과 권리는 각 대회 및 문제 제작자에게 있습니다. 이 저장소의 패키지는 보안 학습 및 스터디용으로 재구성한 자료입니다.

## 문제 출처 및 핵심 취약점

| 주차 | 문제 | 원본문제 | 유형 / 핵심 취약점 | 핵심적으로 익히는 것 |
| --- | --- | --- | --- | --- |
| 2주차 | `Renderer` | scriptCTF 2025 | **Information Disclosure / Broken Access Control** | 정적 경로에 노출된 secret 파일 → 개발자 쿠키 탈취 → 인증 우회 |
| 2주차 | `What` | BCACTF 2025 | **PHP Type Juggling / MD5 Magic Hash** | `==` loose comparison, `0e...` 형태 해시를 이용한 비교 우회 |
| 2주차 | `Wizard Gallery` | scriptCTF 2025 | **File Upload + ImageMagick CVE-2022-44268** | 조작된 이미지 처리 → 서버 로컬 파일 읽기 / 메타데이터를 통한 정보 유출 |
| 3주차 | `CandyCrash` | m0leCon 2026 Beginner | **Node.js VM / Unsafe State Handling** | 게임 replay/state 처리 분석, 서버 로직 악용, VM/debug 기능을 이용한 공격 |
| 3주차 | `Log4baby` | COMPFEST 2022 | **Log4Shell / JNDI Injection** | 사용자 입력이 Log4j에 기록 → `${jndi:...}` 해석 → 외부 객체 로딩/RCE 계열 |
| 4주차 | `Vibecoder` | Welcome CTF 2025 | **JWT Verification Bypass** | JWT 구조 이해, `alg: none`, 서명 검증 실패를 이용한 인증 우회 |
| 4주차 | `Classic Web` | Welcome CTF 2025 | **SQL Injection — SQLite** | 입력값이 SQL 문에 들어가는 구조 분석 → 쿼리 조작 |
| 4주차 | `Spring Function` | CVE Lab | **SpEL Injection / RCE — CVE-2022-22963** | Spring Cloud Function routing expression 악용 → SpEL 표현식 실행 → RCE |
| 5주차 | `baby-jinjail` | idekCTF 2021 | **SSTI / Jinja Sandbox Escape** | Jinja 객체 접근, 필터 우회, 제한된 템플릿 환경 탈출 |
| 5주차 | `file_viewer` | LIT CTF 2025 | **Path Traversal / Arbitrary File Read** | 사용자 입력 경로 조작 → 의도한 디렉터리 밖의 파일 읽기 |
| 5주차 | `fancy-notes` | idekCTF 2021 | **Client-side Prototype Pollution + XS-Leak + Admin Bot** | 취약한 `arg.js` prototype pollution → 이미지 요청을 oracle로 사용 → 관리자 flag note를 문자 단위로 추론 |
| 5주차 | `Mastodon't` | Hack.lu CTF 2023 | **CVE-2023-36460 / Path Traversal → Arbitrary File Write → RCE** | 실제 Mastodon CVE 분석, crafted media, 임의 파일 생성/덮어쓰기, RCE 체인 |
| 6주차 | `SSRF101` | WolvCTF 2022 | **SSRF / Internal Service Access** | 서버 측 요청 기능 분석 → localhost 내부 서비스 접근 → 연쇄 엔드포인트를 통한 flag 읽기 |
| 6주차 | `difference-check` | idekCTF 2021 | **SSRF Filter Bypass** | SSRF 필터 검증 요청과 실제 요청의 차이 분석 → URL 검증/요청 불일치 악용 → 로컬 flag 엔드포인트 접근 |
| 6주차 | `graphql-101` | LINE CTF 2024 | **GraphQL Logic Flaw / Rate Limit Bypass** | GraphQL API 구조, OTP 상태 관리와 rate limit 동작 분석 → WAF 및 요청 제한 우회 → admin 인증 로직 공략 |

## 공통 배포 변경 사항

- `docker compose up --build` 중심의 로컬 실행 환경 구성
- 서비스 포트를 `127.0.0.1`에 바인딩
- 원본 플래그를 `FLAG{T34M_ROOKIE_...}` 형식으로 교체
- 배포 ZIP에 실제 플래그가 평문으로 남지 않도록 난독화 후 컨테이너 실행 시 복원
- 오래된 런타임/의존성은 핵심 취약점 동작을 유지하는 범위에서 현재 Docker 환경에 맞게 조정

문제의 핵심 취약점과 의도된 풀이 흐름은 가능한 한 원본을 유지하는 것을 원칙으로 합니다.

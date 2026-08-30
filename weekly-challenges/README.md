# Weekly Challenges

`weekly-challenges/`에는 T34M ROOKIE 스터디에서 사용하는 주차별 공통 CTF 문제를 보관합니다.

대부분 기존 CTF의 공개 소스 또는 `sajjadium/ctf-archives`에 보존된 문제를 기반으로 하며, 로컬 스터디 환경에서 재현할 수 있도록 Docker 실행 환경, 포트, 플래그 처리 등을 조정했습니다.

> 원본 문제의 저작권과 권리는 각 대회 및 문제 제작자에게 있습니다. 이 저장소의 패키지는 보안 학습 및 스터디용으로 재구성한 자료입니다.

## 문제 출처 및 변형 내역

| 주차 | 문제 | 원본 / 출처 | T34M ROOKIE 변형 내역 |
| --- | --- | --- | --- |
| 2주차 | `Renderer` | scriptCTF 2025 / [`sajjadium/ctf-archives`](https://github.com/sajjadium/ctf-archives) | 원본 웹 문제 로직을 기준으로 로컬 Docker 실행 환경, localhost 포트 바인딩, 스터디용 플래그 처리를 추가했습니다. |
| 2주차 | `What` | BCACTF 2025 / [`sajjadium/ctf-archives`](https://github.com/sajjadium/ctf-archives) | PHP loose comparison 및 MD5 Magic Hash 핵심 로직은 유지하고 Docker 환경과 스터디용 플래그를 적용했습니다. |
| 2주차 | `Wizard Gallery` | scriptCTF 2025 / [`sajjadium/ctf-archives`](https://github.com/sajjadium/ctf-archives) | 원본 파일 업로드/처리 흐름과 취약 ImageMagick 환경을 로컬 Docker에서 재현하도록 구성하고 플래그 경로 및 배포 설정을 조정했습니다. `CVE-2022-44268` 기반입니다. |
| 3주차 | `CandyCrash` | m0leCon 2026 Beginner / [`sajjadium/ctf-archives`](https://github.com/sajjadium/ctf-archives) | Archive에 핵심 백엔드 `CandyCrash.js`는 남아 있었지만 원본 `client/engine.js`와 프론트엔드 파일이 보존되지 않아, 백엔드 세션/리플레이/VM 취약 로직은 유지하고 누락된 match-3 게임 엔진과 프론트엔드는 스터디용으로 복원했습니다. **프론트/엔진은 원본의 완전한 복제본이 아닌 재구성입니다.** |
| 3주차 | `Log4baby` | COMPFEST 2022 / [`sajjadium/ctf-archives`](https://github.com/sajjadium/ctf-archives) | Archive에 보존된 `HomeController.java`와 Log4j 2.14.1 핵심 로깅 로직을 기준으로 실행 가능한 Spring 프로젝트/Docker 환경을 구성했습니다. 주변 프로젝트 파일은 스터디용 재구성입니다. |
| 4주차 | `Vibecoder` | Welcome CTF 2025 공개 문제 소스 | 원본 JWT 검증 실수(`alg: none`)를 유지하고 Docker 실행 환경, 로컬 포트 및 스터디용 플래그 처리를 추가했습니다. |
| 4주차 | `Classic Web` | Welcome CTF 2025 `This is just one of those classic web challenges` 공개 문제 소스 | 원본 SQLite Injection 흐름은 유지했습니다. PHP Docker 환경과 스터디용 플래그를 추가했고, 현재 공식 PHP 이미지에서 이미 제공되는 SQLite 확장을 다시 컴파일하지 않도록 Dockerfile을 조정했습니다. |
| 4주차 | `Spring Function` | Spring Cloud Function `CVE-2022-22963` / [Spring Security Advisory](https://spring.io/security/cve-2022-22963/) | 특정 CTF Archive 원본을 그대로 가져온 문제가 아니라, 취약 버전 Spring Cloud Function의 routing expression / SpEL Injection 동작을 로컬에서 학습할 수 있도록 만든 **교육용 재구성 문제**입니다. |
| 5주차 | `baby-jinjail` | idekCTF 2021 / [`ctf-archives`](https://github.com/sajjadium/ctf-archives/tree/main/ctfs/idekCTF/2021/web/baby-jinjail) | Archive의 원본 `app.py`와 템플릿을 그대로 사용하고 Docker 배포 래퍼, localhost 포트, 스터디용 플래그 처리만 추가했습니다. |
| 5주차 | `file_viewer` | Lexington Informatics Tournament CTF 2025 / [`ctf-archives`](https://github.com/sajjadium/ctf-archives/tree/main/ctfs/LexingtonInformaticsTournament/2025/web/file_viewer) | Archive의 원본 `app.py`를 그대로 사용합니다. 원본에 별도 Docker 환경이 없어 Dockerfile, 샘플 파일, 로컬 포트 및 스터디용 플래그 처리를 추가했습니다. |
| 5주차 | `Mastodon't` | Hack.lu CTF 2023 / [`ctf-archives`](https://github.com/sajjadium/ctf-archives/tree/main/ctfs/Hack.lu/2023/web/Mastodont) | 원본이 지정한 취약 Mastodon 소스, ImageMagick, `readflag`, s6 초기화 구조를 유지합니다. 빌드 시 `ctf-archives`의 고정 커밋에서 원본 소스를 가져오며 로컬 포트, 스터디용 플래그, 현재 Debian에서 실패할 수 있는 일부 배포 단계를 조정했습니다. `CVE-2023-36460` 기반입니다. |
| 5주차 | `fancy-notes` | idekCTF 2021 / [`ctf-archives`](https://github.com/sajjadium/ctf-archives/tree/main/ctfs/idekCTF/2021/web/fancy-notes) | 원본 `app.py`, 템플릿, 정적 파일, `bot.js`를 그대로 사용합니다. 오래된 Chrome/Puppeteer Docker 환경을 현재 환경에서 빌드 가능하도록 Chromium/Python 기반 배포 래퍼로 조정하고 로컬 포트와 스터디용 플래그 처리를 추가했습니다. |

## 공통 배포 변경 사항

- `docker compose up --build` 중심의 로컬 실행 환경 구성
- 서비스 포트를 `127.0.0.1`에 바인딩
- 원본 플래그를 `FLAG{T34M_ROOKIE_...}` 형식으로 교체
- 배포 ZIP에 실제 플래그가 평문으로 남지 않도록 난독화 후 컨테이너 실행 시 복원
- 오래된 런타임/의존성은 핵심 취약점 동작을 유지하는 범위에서 현재 Docker 환경에 맞게 조정

문제의 핵심 취약점과 의도된 풀이 흐름은 가능한 한 원본을 유지하는 것을 원칙으로 합니다.

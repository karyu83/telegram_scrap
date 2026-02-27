# TICC — Telegram Investment Channel Collector

텔레그램 투자 채널의 메시지를 실시간으로 수집하여 로컬 파일에 저장하는 시스템입니다.

> **권한 제한 환경 주의**: 이 프로젝트는 일반 사용자 권한(비관리자)으로 완전히 동작하도록 설계되었습니다.
> `sudo`, 관리자 권한, 시스템 수준 설치 없이 실행 가능합니다.

---

## 목차

1. [개요](#개요)
2. [아키텍처](#아키텍처)
3. [사전 준비](#사전-준비)
4. [설치](#설치)
5. [설정](#설정)
6. [채널 관리](#채널-관리)
7. [실행](#실행)
8. [데이터 구조](#데이터-구조)
9. [로그 확인](#로그-확인)
10. [테스트](#테스트)
11. [문제 해결](#문제-해결)

---

## 개요

### 무엇을 하는가

- 텔레그램 투자 채널에 새 메시지가 올라오면 **즉시** 로컬 파일로 저장
- **봇 권한 없이** 동작 (Telegram User API 사용 — 일반 계정으로 읽기)
- 연결이 끊겨도 **자동 재연결** + 누락된 메시지 보충 수집
- 메시지 텍스트, 미디어 첨부, 조회수 등 구조화된 형태로 저장

### 동작 모드

| 모드 | 설명 | 사용 상황 |
|------|------|---------|
| **realtime** | 신규 메시지를 이벤트로 즉시 수신 | 평상시 상시 실행 |
| **batch** | 주기적으로 과거 메시지를 보충 수집 | realtime 보조, 누락 복구 |

---

## 아키텍처

```
channels.json          .env
    │                   │
    ▼                   ▼
channel_manager    config / logger
    │                   │
    └─────────┬─────────┘
              │
           client.py  ◄── Telegram API (Telethon)
              │
    ┌─────────┴─────────┐
    ▼                   ▼
collector.py      batch_collector.py
(실시간 수신)      (누락 보충)
    │                   │
    ▼                   ▼
message_parser.py       │
    │                   │
    ├── media_downloader.py
    │
    ▼
storage.py  ──► data/{alias}/{YYYY-MM-DD}.jsonl
    │
metadata.py ──► data/_metadata.json
```

### 주요 모듈

| 파일 | 역할 |
|------|------|
| `src/config.py` | `.env` 환경변수 로드 |
| `src/channel_manager.py` | `channels.json` 채널 목록 파싱 및 resolve |
| `src/channel_registry.py` | 채널 추가/중복 검사 |
| `src/channel_cli.py` | 채널 관리 CLI |
| `src/client.py` | Telethon 클라이언트 생성/연결 |
| `src/collector.py` | 실시간 이벤트 핸들러 |
| `src/batch_collector.py` | 과거 메시지 배치 수집 |
| `src/message_parser.py` | 메시지 → 딕셔너리 변환 |
| `src/storage.py` | JSONL 파일 쓰기, 중복 방지 |
| `src/media_downloader.py` | 미디어 파일 다운로드 |
| `src/metadata.py` | 채널별 수집 상태 추적 |
| `src/reconnect.py` | 재연결 + 지수 백오프 |
| `src/logger.py` | 로그 설정 (콘솔 + 파일) |
| `src/run.py` | 실행 진입점 (argparse) |
| `src/main.py` | 이벤트 핸들러 등록, `-m src.main` 진입점 |

---

## 사전 준비

### 1. Python 3.9 이상

```bash
python --version   # 3.9+ 확인
```

### 2. Telegram API 키 발급

1. [https://my.telegram.org/apps](https://my.telegram.org/apps) 접속 (본인 계정 로그인)
2. **Create new application** 클릭
3. `api_id` (숫자)와 `api_hash` (32자리 문자열) 발급
4. 이 두 값은 `.env` 파일에 저장됩니다 (아래 [설정](#설정) 참조)

> 봇 토큰이 **아닙니다**. 일반 사용자 계정 API 키를 발급받아야 합니다.

---

## 설치

```bash
# 1. 저장소 클론
git clone <repo-url>
cd telegram_scrap

# 2. 가상환경 생성 (권장 — 시스템 Python 오염 방지)
python -m venv .venv

# 3. 가상환경 활성화
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. (선택) 개발/테스트용 패키지
pip install -r requirements-dev.txt
```

---

## 설정

### `.env` 파일 생성

```bash
cp .env.example .env
```

`.env` 파일을 열어 값을 채워 넣습니다:

```env
# 필수: Telegram API 인증 정보
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+821012345678

# 선택: 기본값이 있는 설정
DOWNLOAD_MEDIA=true          # 미디어 파일 다운로드 여부 (기본: true)
MEDIA_MAX_SIZE_MB=50         # 다운로드 최대 파일 크기 MB (기본: 50)
BATCH_INTERVAL_SEC=300       # 배치 수집 주기 초 (기본: 300 = 5분)
LOG_LEVEL=INFO               # 로그 레벨: DEBUG / INFO / WARNING / ERROR
DATA_DIR=data                # 데이터 저장 루트 디렉토리 (기본: data)
```

> `.env` 파일은 `.gitignore`에 포함되어 있어 버전 관리에 업로드되지 않습니다.

### 최초 실행 시 인증

처음 실행하면 전화번호 인증이 필요합니다:

1. 프로그램이 실행되면 Telegram에서 인증 코드 SMS/앱 알림이 전송됩니다
2. 터미널에 코드를 입력합니다
3. 인증 성공 시 `session/` 디렉토리에 세션 파일이 생성됩니다
4. 이후 실행부터는 세션 파일을 재사용하므로 재인증 불필요

> 세션 파일도 `.gitignore`에 포함되어 있습니다.

---

## 채널 관리

### `channels.json` 파일 구조

```json
{
  "channels": [
    {
      "alias": "투자뉴스A",
      "username": "investnews_kr",
      "enabled": true
    },
    {
      "alias": "해외주식속보",
      "id": -1001234567890,
      "enabled": true
    },
    {
      "alias": "비활성채널",
      "username": "some_channel",
      "enabled": false
    }
  ]
}
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `alias` | ✅ | 채널 별칭 (폴더명, 로그 표시용) |
| `username` | 둘 중 하나 | 공개 채널의 `@username` (@ 제외) |
| `id` | 둘 중 하나 | 비공개 채널의 채널 ID (음수 정수) |
| `enabled` | ✅ | `true`/`false` — `false`면 수집 대상 제외 |

### CLI로 채널 추가

```bash
# 공개 채널 추가
python -m src.channel_cli add --alias "투자뉴스A" --username investnews_kr

# 비공개 채널 추가 (채널 ID)
python -m src.channel_cli add --alias "해외주식속보" --id -1001234567890

# 비활성 상태로 추가
python -m src.channel_cli add --alias "임시채널" --username some_ch --disabled

# 다른 파일 경로 지정
python -m src.channel_cli add --channels-file custom_channels.json --alias "테스트" --username testch
```

> 중복 alias 또는 중복 username/id 입력 시 오류가 발생합니다.

---

## 실행

### 기본 실행 (실시간 모드)

```bash
python -m src.main
```

또는

```bash
python -m src.run --mode realtime
```

### 배치 모드 실행

```bash
python -m src.run --mode batch
```

### 옵션 전체

```
python -m src.run [OPTIONS]

옵션:
  --mode {realtime,batch}         실행 모드 (기본: realtime)
  --channels-file PATH            채널 설정 파일 경로 (기본: channels.json)
  --metadata-path PATH            메타데이터 파일 경로 (기본: data/_metadata.json)
```

### 예시

```bash
# 실시간 수집, 커스텀 채널 파일
python -m src.run --mode realtime --channels-file my_channels.json

# 배치 수집, 커스텀 메타데이터 경로
python -m src.run --mode batch --metadata-path /path/to/metadata.json

# 백그라운드 실행 (Linux/macOS)
nohup python -m src.main > /dev/null 2>&1 &

# 백그라운드 실행 (Windows)
start /B python -m src.main
```

### 종료

`Ctrl + C`로 종료합니다. 진행 중인 메시지 처리가 완료된 후 종료됩니다.

---

## 데이터 구조

### 파일 레이아웃

```
data/
├── _metadata.json              # 채널별 수집 상태 (마지막 메시지 ID 등)
├── 투자뉴스A/
│   ├── 2026-02-27.jsonl        # 날짜별 메시지 (JSON Lines)
│   ├── 2026-02-26.jsonl
│   └── media/
│       ├── 12345_photo.jpg     # {message_id}_{filename}
│       └── 12346_document.pdf
└── 해외주식속보/
    └── 2026-02-27.jsonl
```

### 메시지 레코드 (`*.jsonl` 각 줄)

```json
{
  "message_id": 45232,
  "channel_id": -1001234567890,
  "channel_alias": "투자뉴스A",
  "date": "2026-02-27T09:15:00+00:00",
  "text": "삼성전자 목표주가 상향 조정...",
  "has_media": true,
  "media_type": "photo",
  "media_file": "45232_photo.jpg",
  "views": 1523,
  "forwards": 42,
  "edit_date": null,
  "is_edit": false,
  "collected_at": "2026-02-27T18:15:01.654321"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `message_id` | int | 텔레그램 메시지 고유 ID |
| `channel_id` | int | 채널 ID |
| `channel_alias` | str | `channels.json`에 지정한 별칭 |
| `date` | str (ISO8601 UTC) | 메시지 게시 시각 |
| `text` | str | 본문 또는 캡션 (없으면 빈 문자열) |
| `has_media` | bool | 미디어 첨부 여부 |
| `media_type` | str\|null | `"photo"` / `"document"` / `"video"` / `null` |
| `media_file` | str\|null | 저장된 미디어 파일명 (미다운로드 시 `null`) |
| `views` | int\|null | 조회수 |
| `forwards` | int\|null | 전달 수 |
| `edit_date` | str\|null | 편집 시각 (ISO8601 UTC) |
| `is_edit` | bool | 편집된 메시지 여부 |
| `collected_at` | str (ISO8601) | 수집 시각 (로컬 시간) |

### 메타데이터 (`data/_metadata.json`)

```json
{
  "투자뉴스A": {
    "last_message_id": 45232,
    "last_collected_at": "2026-02-27T18:15:01.654321",
    "total_collected": 1523
  }
}
```

---

## 로그 확인

로그는 콘솔과 파일에 동시 출력됩니다.

```
logs/
└── collector_2026-02-27.log    # 일별 자동 분리
```

**로그 형식**:
```
2026-02-27 18:15:01,234 [INFO] [collector] New message 45232 from 투자뉴스A
2026-02-27 18:15:01,456 [INFO] [storage] Saved message 45232 to data/투자뉴스A/2026-02-27.jsonl
2026-02-27 18:20:00,000 [WARNING] [reconnect] Connection lost, retrying in 30s
2026-02-27 18:20:31,500 [INFO] [reconnect] Reconnected successfully
```

---

## 테스트

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=term-missing

# 특정 모듈만
pytest tests/test_message_parser.py -v
pytest tests/test_storage.py -v

# 조용히 실행 (실패만 출력)
pytest tests/ -q
```

현재 테스트 수: **84개** (전체 통과)
목표 커버리지: **90% 이상** (핵심 모듈 95% 이상)

---

## 문제 해결

### 자주 발생하는 오류

**`Required environment variable missing: TELEGRAM_API_ID`**
→ `.env` 파일이 없거나 값이 비어 있습니다. [설정](#설정) 단계를 확인하세요.

**`SessionPasswordNeededError`**
→ 2단계 인증(2FA)이 활성화된 계정입니다. 텔레그램 앱에서 2FA 비밀번호를 입력해야 합니다.

**`FloodWaitError: X seconds`**
→ 텔레그램 API 요청 한도 초과. 프로그램이 자동으로 대기 후 재시도합니다.

**채널 메시지가 수집되지 않음**
→ `channels.json`에서 해당 채널의 `"enabled": true` 여부와 `username`/`id` 값을 확인하세요.
→ 해당 텔레그램 계정이 채널에 **구독(참여)** 상태인지 확인하세요.

**`session/` 디렉토리가 없다는 오류**
→ 자동 생성됩니다. 수동으로 `mkdir session` 실행해도 됩니다.

### 디렉토리 초기화

처음 실행 전 아래 디렉토리가 자동 생성됩니다:
- `session/` — 세션 파일
- `data/` — 수집 데이터
- `logs/` — 로그 파일

수동으로 만들어도 됩니다:
```bash
mkdir -p session data logs
```

---

## 보안 유의사항

- `.env` 파일에는 API 키와 전화번호가 포함됩니다. **절대 버전 관리(git)에 커밋하지 마세요.**
- `session/` 디렉토리의 세션 파일도 **공유하지 마세요** (계정 탈취 위험).
- 수집된 데이터는 **개인 투자 참고 용도**로만 사용하며 Telegram 이용약관을 준수하세요.
- 과도한 API 호출은 계정 제한의 원인이 됩니다. 기본 배치 간격(5분)을 유지하세요.

---

## 프로젝트 구조

```
telegram_scrap/
├── .env.example            # 환경변수 템플릿
├── .gitignore
├── README.md
├── requirements.txt        # 실행 의존성
├── requirements-dev.txt    # 개발/테스트 의존성
├── channels.json           # 채널 목록 설정 (직접 생성)
├── plan.md                 # TDD 개발 계획
├── PRD.md                  # 제품 요구사항 문서
│
├── src/
│   ├── config.py           # 환경변수 로드
│   ├── logger.py           # 로깅 설정
│   ├── metadata.py         # 수집 상태 추적
│   ├── message_parser.py   # 메시지 파싱
│   ├── storage.py          # JSONL 저장
│   ├── channel_manager.py  # 채널 목록 관리
│   ├── channel_registry.py # 채널 추가/중복 검사
│   ├── channel_cli.py      # 채널 관리 CLI
│   ├── reconnect.py        # 재연결/백오프
│   ├── client.py           # Telethon 클라이언트
│   ├── media_downloader.py # 미디어 다운로드
│   ├── collector.py        # 실시간 핸들러
│   ├── batch_collector.py  # 배치 수집
│   ├── batch.py            # 배치 실행 루프
│   ├── run.py              # 실행 진입점
│   └── main.py             # 모듈 실행 진입점
│
├── tests/
│   ├── conftest.py         # 공용 테스트 fixture
│   ├── test_config.py
│   ├── test_storage.py
│   ├── test_channel_manager.py
│   ├── test_collector.py
│   ├── test_batch_collector.py
│   ├── test_media_downloader.py
│   ├── test_integration.py
│   └── test_main.py
│
├── session/                # 세션 파일 (.gitignore)
├── data/                   # 수집 데이터 (.gitignore)
└── logs/                   # 로그 파일 (.gitignore)
```

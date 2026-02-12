# PRD: 텔레그램 투자 채널 메시지 수집 시스템

## 문서 정보

| 항목 | 내용 |
|------|------|
| 프로젝트명 | Telegram Investment Channel Collector (TICC) |
| 버전 | 1.0.0 |
| 작성일 | 2026-02-11 |
| 개발 방식 | TDD (Test-Driven Development) |
| 주요 언어 | Python 3.9+ |

---

## 1. 프로젝트 개요

### 1.1 목적

텔레그램 투자 관련 채널(타인 운영, 공개/구독 채널)에 새 메시지가 게시될 때 이를 실시간으로 수신하여 로컬 파일 시스템에 구조화된 형태로 저장하는 시스템을 구축한다.

### 1.2 배경

- 주식 투자에 활용할 목적으로, 여러 투자 뉴스/분석 채널의 메시지를 통합 수집
- 봇 관리자 권한이 없는 타인 채널이 대상이므로 Telegram User Client API (Telethon) 사용
- 수집된 데이터는 개인 투자 참고 용도로만 활용

### 1.3 핵심 가치

- **실시간성**: 메시지 게시 즉시 수신 및 저장
- **안정성**: 연결 끊김, 에러 상황에서 자동 복구
- **무결성**: 메시지 누락 없이 완전한 수집 보장

---

## 2. 기술 스택

| 구분 | 기술 | 비고 |
|------|------|------|
| 언어 | Python 3.9+ | |
| Telegram API | Telethon | User Client API |
| 테스트 | pytest + pytest-asyncio | 비동기 테스트 지원 |
| 모킹 | unittest.mock / pytest-mock | Telethon 모킹 |
| 설정 관리 | python-dotenv | 환경변수 기반 |
| 로깅 | Python logging (stdlib) | |
| 데이터 포맷 | JSON Lines (.jsonl) | append 친화적 |

---

## 3. 기능 요구사항

### FR-01: 텔레그램 클라이언트 인증 및 연결

**설명**: Telegram User API를 통해 사용자 계정으로 인증하고 세션을 유지한다.

**인수 조건**:
- AC-01-1: `api_id`, `api_hash`, `phone` 으로 Telethon 클라이언트가 생성된다.
- AC-01-2: 최초 실행 시 전화번호 인증 후 세션 파일이 `session/` 디렉토리에 저장된다.
- AC-01-3: 이후 실행 시 세션 파일을 재사용하여 재인증 없이 연결된다.
- AC-01-4: 인증 정보(api_id, api_hash, phone)는 `.env` 파일에서 로드된다.

**테스트 전략**:
- 단위 테스트: 설정 로드 로직, 클라이언트 생성 파라미터 검증
- 통합 테스트: 실제 연결은 수동 테스트 (API 키 필요)

---

### FR-02: 채널 등록 및 관리

**설명**: 모니터링할 채널 목록을 설정 파일로 관리하고, 채널 엔티티를 resolve 한다.

**인수 조건**:
- AC-02-1: `config.py` 또는 `channels.json`에 채널 목록을 정의할 수 있다.
- AC-02-2: 공개 채널은 `username`, 비공개 채널은 `channel_id`로 식별한다.
- AC-02-3: 채널 resolve 실패 시 에러 로그를 남기고 나머지 채널은 정상 등록한다.
- AC-02-4: 채널별 별칭(alias)을 지정할 수 있다 (폴더명, 로그 표시용).

**입력 형식 예시**:
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
    }
  ]
}
```

**테스트 전략**:
- 단위 테스트: 채널 설정 파싱, 유효성 검증, 활성/비활성 필터링

---

### FR-03: 실시간 메시지 수신 (Primary Mode)

**설명**: 등록된 채널에 새 메시지가 게시되면 이벤트를 즉시 수신한다.

**인수 조건**:
- AC-03-1: Telethon `events.NewMessage`를 사용하여 등록된 채널의 메시지를 실시간 수신한다.
- AC-03-2: 텍스트 메시지, 미디어 첨부 메시지, 캡션 포함 메시지를 모두 수신한다.
- AC-03-3: 수신된 메시지는 즉시 저장 파이프라인으로 전달된다.
- AC-03-4: 편집된 메시지(edit)도 감지하여 저장한다 (`events.MessageEdited`).

**테스트 전략**:
- 단위 테스트: 이벤트 핸들러가 올바른 데이터를 추출하는지 검증 (모킹)
- 단위 테스트: 등록되지 않은 채널의 메시지는 무시하는지 검증

---

### FR-04: 배치 수집 (Secondary Mode / 보충)

**설명**: 실시간 수신이 끊겼던 기간의 누락 메시지를 보충 수집한다.

**인수 조건**:
- AC-04-1: 각 채널별 마지막 수집 `message_id`를 `_metadata.json`에 기록한다.
- AC-04-2: 배치 실행 시 `min_id` 이후의 메시지를 일괄 조회한다.
- AC-04-3: 이미 저장된 메시지는 중복 저장하지 않는다.
- AC-04-4: 설정 가능한 간격(기본 5분)으로 주기적 실행을 지원한다.
- AC-04-5: 한 번 조회 시 최대 100개 메시지를 가져온다 (Telegram API 제한 준수).

**테스트 전략**:
- 단위 테스트: 메타데이터 읽기/쓰기, 중복 판별 로직
- 단위 테스트: min_id 기반 조회 파라미터 구성 검증

---

### FR-05: 메시지 파싱 및 데이터 구조화

**설명**: 수신된 Telethon 메시지 객체를 저장용 딕셔너리로 변환한다.

**인수 조건**:
- AC-05-1: 다음 필드를 추출하여 구조화한다:

| 필드 | 타입 | 설명 |
|------|------|------|
| `message_id` | int | 메시지 고유 ID |
| `channel_id` | int | 채널 ID |
| `channel_alias` | str | 채널 별칭 |
| `date` | str (ISO8601) | 메시지 게시 시각 (UTC) |
| `text` | str | 메시지 본문 (텍스트 또는 캡션) |
| `has_media` | bool | 미디어 포함 여부 |
| `media_type` | str \| null | photo / document / video / null |
| `media_file` | str \| null | 저장된 미디어 파일명 |
| `views` | int \| null | 조회수 |
| `forwards` | int \| null | 전달 수 |
| `edit_date` | str \| null | 편집 시각 (ISO8601) |
| `is_edit` | bool | 편집된 메시지 여부 |
| `collected_at` | str (ISO8601) | 수집 시각 (로컬) |

- AC-05-2: `text`가 None인 경우 빈 문자열로 처리한다.
- AC-05-3: `date` 필드는 항상 UTC ISO8601 형식이다.
- AC-05-4: 파싱 실패 시 에러 로그를 남기고 원본 메시지 ID를 기록한다.

**테스트 전략**:
- 단위 테스트: 다양한 메시지 유형별 파싱 결과 검증 (텍스트만, 사진+캡션, 문서, 미디어만 등)
- 단위 테스트: None/빈값 엣지케이스 처리 검증

---

### FR-06: 로컬 파일 저장

**설명**: 구조화된 메시지를 채널별/날짜별 JSON Lines 파일로 저장한다.

**인수 조건**:
- AC-06-1: 저장 경로: `data/{channel_alias}/{YYYY-MM-DD}.jsonl`
- AC-06-2: 파일이 없으면 새로 생성, 있으면 append 한다.
- AC-06-3: 인코딩은 UTF-8, `ensure_ascii=False`로 한국어 원문 보존.
- AC-06-4: 한 줄에 하나의 JSON 객체 (JSON Lines 형식).
- AC-06-5: 파일 쓰기 실패 시 최대 3회 재시도 후 에러 로그를 남긴다.
- AC-06-6: 동일 `message_id`가 이미 파일에 존재하면 저장하지 않는다 (중복 방지).

**테스트 전략**:
- 단위 테스트: 파일 생성, append, 중복 방지, 인코딩 검증
- 단위 테스트: 디렉토리 자동 생성, 파일 쓰기 재시도 로직
- 단위 테스트: JSONL 포맷 정합성 (각 줄이 valid JSON인지)

---

### FR-07: 미디어 파일 다운로드

**설명**: 메시지에 첨부된 미디어(사진, 문서, 영상)를 로컬에 다운로드한다.

**인수 조건**:
- AC-07-1: 미디어 저장 경로: `data/{channel_alias}/media/{message_id}_{원본파일명}`
- AC-07-2: 사진은 최고 해상도 버전을 다운로드한다.
- AC-07-3: 다운로드 실패 시 에러 로그를 남기되, 텍스트 저장은 정상 진행한다.
- AC-07-4: 미디어 다운로드 ON/OFF를 설정에서 제어할 수 있다 (`DOWNLOAD_MEDIA`).
- AC-07-5: 대용량 파일(50MB 초과) 다운로드는 건너뛰고 로그에 기록한다.

**테스트 전략**:
- 단위 테스트: 미디어 타입별 파일 경로 생성 로직
- 단위 테스트: 파일 크기 초과 시 스킵 로직
- 단위 테스트: 다운로드 실패 시 텍스트 저장 독립성 검증

---

### FR-08: 메타데이터 관리

**설명**: 각 채널별 수집 상태를 추적하여 누락 방지 및 재시작 복구를 지원한다.

**인수 조건**:
- AC-08-1: `data/_metadata.json`에 채널별 마지막 수집 정보를 기록한다.
- AC-08-2: 기록 항목: `last_message_id`, `last_collected_at`, `total_collected`
- AC-08-3: 메시지 저장 성공 시마다 메타데이터를 업데이트한다.
- AC-08-4: 메타데이터 파일이 없거나 손상되었을 때 빈 상태로 초기화한다.

**메타데이터 형식**:
```json
{
  "investnews_kr": {
    "last_message_id": 45232,
    "last_collected_at": "2026-02-11T18:15:01.654321",
    "total_collected": 1523
  }
}
```

**테스트 전략**:
- 단위 테스트: 메타데이터 CRUD, 파일 손상 복구, 동시 쓰기 안전성

---

### FR-09: 연결 관리 및 자동 재연결

**설명**: 네트워크 단절, 텔레그램 서버 점검 등의 상황에서 자동으로 재연결한다.

**인수 조건**:
- AC-09-1: 연결 끊김 감지 시 30초 대기 후 재연결을 시도한다.
- AC-09-2: 재연결 실패 시 지수 백오프(30초 → 60초 → 120초 → 최대 300초)로 재시도한다.
- AC-09-3: 재연결 성공 시 배치 수집을 1회 실행하여 끊김 기간의 누락 메시지를 보충한다.
- AC-09-4: `FloodWaitError` 발생 시 텔레그램이 요구하는 대기 시간만큼 sleep 한다.
- AC-09-5: 연결 상태 변화를 로그에 기록한다.

**테스트 전략**:
- 단위 테스트: 지수 백오프 계산 로직
- 단위 테스트: FloodWaitError 대기 시간 처리
- 단위 테스트: 재연결 후 배치 수집 트리거 검증

---

### FR-10: 로깅

**설명**: 시스템 전반의 동작 상태를 구조화된 로그로 기록한다.

**인수 조건**:
- AC-10-1: 로그 파일 경로: `logs/collector_{YYYY-MM-DD}.log` (일별 로테이션).
- AC-10-2: 콘솔(stdout)과 파일 동시 출력.
- AC-10-3: 로그 레벨: DEBUG, INFO, WARNING, ERROR.
- AC-10-4: 로그 형식: `{timestamp} [{level}] [{module}] {message}`
- AC-10-5: 메시지 수신/저장 시 INFO, 에러 시 ERROR + traceback.

**테스트 전략**:
- 단위 테스트: 로그 포맷 검증, 일별 로테이션 파일명 생성

---

## 4. 비기능 요구사항

### NFR-01: 성능

- 메시지 수신 → 파일 저장 완료까지 2초 이내 (미디어 다운로드 제외).
- 동시 10개 채널 모니터링 시에도 안정적 동작.

### NFR-02: 안정성

- 24시간 무중단 실행이 가능해야 한다.
- 비정상 종료 후 재시작 시 데이터 손실이 없어야 한다.

### NFR-03: 보안

- API 키, 전화번호는 `.env` 파일에만 저장하고 버전 관리에 포함하지 않는다.
- 세션 파일은 `.gitignore`에 포함한다.

### NFR-04: 확장성

- 새 채널 추가 시 설정 파일 수정만으로 가능해야 한다.
- 향후 저장소를 DB로 변경할 수 있도록 저장 레이어를 분리한다.

### NFR-05: Telegram 이용약관 준수

- 과도한 API 호출을 자제한다 (Rate Limit 준수).
- 수집 데이터는 개인 투자 참고 용도로만 사용한다.

---

## 5. 프로젝트 구조

```
telegram-investment-collector/
├── .env.example            # 환경변수 템플릿
├── .gitignore
├── README.md
├── requirements.txt
├── channels.json           # 채널 목록 설정
│
├── src/
│   ├── __init__.py
│   ├── config.py           # 설정 로드
│   ├── client.py           # Telethon 클라이언트 생성 및 연결 관리
│   ├── channel_manager.py  # 채널 등록/resolve
│   ├── collector.py        # 실시간 메시지 수신 핸들러
│   ├── batch_collector.py  # 배치 보충 수집
│   ├── message_parser.py   # 메시지 파싱/구조화
│   ├── storage.py          # 파일 저장 (JSONL)
│   ├── media_downloader.py # 미디어 다운로드
│   ├── metadata.py         # 메타데이터 관리
│   ├── reconnect.py        # 재연결 및 백오프 로직
│   └── logger.py           # 로깅 설정
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # 공용 fixture (모킹된 메시지 객체 등)
│   ├── test_config.py
│   ├── test_channel_manager.py
│   ├── test_collector.py
│   ├── test_batch_collector.py
│   ├── test_message_parser.py
│   ├── test_storage.py
│   ├── test_media_downloader.py
│   ├── test_metadata.py
│   ├── test_reconnect.py
│   └── test_logger.py
│
├── session/                # 세션 파일 (gitignore)
├── data/                   # 수집 데이터 (gitignore)
└── logs/                   # 로그 파일 (gitignore)
```

---

## 6. TDD 개발 순서

Red-Green-Refactor 사이클을 준수하며, 다음 순서로 구현한다.

### Phase 1: 기반 (의존성 없는 순수 로직)

| 순서 | 모듈 | 관련 FR | 핵심 테스트 케이스 |
|------|------|---------|-------------------|
| 1 | `config.py` | FR-01 | 환경변수 로드, 필수값 누락 시 에러 |
| 2 | `logger.py` | FR-10 | 로그 포맷, 파일 로테이션 |
| 3 | `metadata.py` | FR-08 | CRUD, 파일 손상 복구, 초기화 |
| 4 | `message_parser.py` | FR-05 | 메시지 유형별 파싱, 엣지케이스 |
| 5 | `storage.py` | FR-06 | JSONL 쓰기, 중복 방지, 재시도 |

### Phase 2: 채널/연결 관리

| 순서 | 모듈 | 관련 FR | 핵심 테스트 케이스 |
|------|------|---------|-------------------|
| 6 | `channel_manager.py` | FR-02 | 설정 파싱, resolve 실패 처리 |
| 7 | `reconnect.py` | FR-09 | 지수 백오프, FloodWait 처리 |
| 8 | `client.py` | FR-01 | 클라이언트 생성 파라미터 |

### Phase 3: 수집 기능

| 순서 | 모듈 | 관련 FR | 핵심 테스트 케이스 |
|------|------|---------|-------------------|
| 9 | `media_downloader.py` | FR-07 | 경로 생성, 크기 초과 스킵, 실패 격리 |
| 10 | `collector.py` | FR-03 | 이벤트 핸들링, 파이프라인 연동 |
| 11 | `batch_collector.py` | FR-04 | min_id 조회, 중복 방지 |

### Phase 4: 통합 및 안정화

| 순서 | 작업 | 내용 |
|------|------|------|
| 12 | 통합 테스트 | 수신 → 파싱 → 저장 전체 파이프라인 |
| 13 | main.py / batch.py | 진입점 작성 (실시간/배치) |
| 14 | 수동 통합 테스트 | 실제 텔레그램 연결 테스트 |

---

## 7. 테스트 전략

### 7.1 테스트 유형

| 유형 | 비율 | 대상 |
|------|------|------|
| 단위 테스트 | 80% | 개별 모듈의 순수 로직 |
| 통합 테스트 | 15% | 모듈 간 연동 (모킹된 Telethon) |
| 수동 테스트 | 5% | 실제 텔레그램 API 연결 |

### 7.2 모킹 전략

Telethon의 외부 의존성은 모두 모킹하되, 내부 로직은 실제로 실행한다.

```python
# conftest.py 예시
@pytest.fixture
def mock_message():
    """Telethon Message 객체 모킹"""
    msg = MagicMock()
    msg.id = 12345
    msg.text = "테스트 메시지"
    msg.date = datetime(2026, 2, 11, 9, 0, 0, tzinfo=timezone.utc)
    msg.media = None
    msg.views = 100
    msg.forwards = 5
    msg.edit_date = None
    return msg

@pytest.fixture
def mock_channel():
    """Telethon Channel 엔티티 모킹"""
    ch = MagicMock()
    ch.id = -1001234567890
    ch.username = "investnews_kr"
    ch.title = "투자뉴스A"
    return ch
```

### 7.3 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=term-missing

# 특정 모듈만
pytest tests/test_message_parser.py -v

# 비동기 테스트
pytest tests/test_collector.py -v  # pytest-asyncio 자동 감지
```

### 7.4 커버리지 목표

- 전체: **90% 이상**
- 핵심 모듈 (message_parser, storage, metadata): **95% 이상**

---

## 8. 의존성 패키지

### requirements.txt

```
telethon>=1.36.0
python-dotenv>=1.0.0
```

### requirements-dev.txt

```
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0
pytest-cov>=4.1.0
```

---

## 9. 설정 파일 명세

### .env.example

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+821012345678
DOWNLOAD_MEDIA=true
MEDIA_MAX_SIZE_MB=50
BATCH_INTERVAL_SEC=300
LOG_LEVEL=INFO
DATA_DIR=data
```

### .gitignore

```
.env
session/
data/
logs/
__pycache__/
*.pyc
.pytest_cache/
.coverage
```

---

## 10. 향후 확장 고려사항 (Backlog)

| 우선순위 | 기능 | 설명 |
|---------|------|------|
| P1 | 키워드 필터링 | 특정 종목/키워드 포함 메시지만 별도 알림 |
| P1 | 데스크톱 알림 | 중요 메시지 수신 시 시스템 알림 |
| P2 | SQLite 저장소 | JSONL → SQLite로 변경하여 검색 편의 강화 |
| P2 | 웹 대시보드 | 수집된 메시지 조회/검색 UI |
| P3 | 감성 분석 | 메시지 긍/부정 판단 (LLM 연동) |
| P3 | 자동 요약 | 일별/주별 채널 메시지 요약 리포트 |

---

## 11. Claude Code 개발 가이드라인

Claude Code에서 본 PRD를 기반으로 개발 시 아래 원칙을 따른다.

### TDD 사이클

1. **Red**: 실패하는 테스트를 먼저 작성한다.
2. **Green**: 테스트를 통과하는 최소한의 코드를 구현한다.
3. **Refactor**: 코드를 정리하되 테스트가 계속 통과하는지 확인한다.

### 개발 명령 예시

```bash
# Phase 1부터 순서대로 진행
# 1. 테스트 먼저 작성
# 2. 구현
# 3. 테스트 통과 확인
# 4. 리팩토링
# 5. 다음 모듈로 이동

pytest tests/test_config.py -v          # Phase 1-1
pytest tests/test_message_parser.py -v  # Phase 1-4
pytest tests/ -v --cov=src              # 전체 확인
```

### 주요 규칙

- 모든 모듈은 반드시 대응하는 테스트 파일이 있어야 한다.
- 외부 API(Telethon)는 항상 모킹한다.
- 파일 I/O 테스트는 `tmp_path` fixture를 사용한다.
- 비동기 함수 테스트는 `@pytest.mark.asyncio`를 사용한다.
- 한국어 텍스트 처리 테스트 케이스를 반드시 포함한다.

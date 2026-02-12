# TICC 개발 계획 (TDD)

각 테스트 항목을 순서대로 진행한다. "go" 명령 시 다음 미체크 항목의 테스트를 작성하고, 통과할 최소 코드를 구현한다.

- `[ ]` = 미완료, `[x]` = 완료
- 각 항목: Red(테스트 작성) → Green(최소 구현) → Refactor

---

## Phase 0: 프로젝트 셋업

- [x] 0-1. 프로젝트 디렉토리 구조 생성 (`src/`, `tests/`, `session/`, `data/`, `logs/`)
- [x] 0-2. `requirements.txt`, `requirements-dev.txt` 생성
- [x] 0-3. `.env.example`, `.gitignore` 생성
- [x] 0-4. `src/__init__.py`, `tests/__init__.py`, `tests/conftest.py` (공용 fixture) 생성
- [x] 0-5. pytest 실행 확인 (빈 테스트 통과)

---

## Phase 1: 기반 모듈 (순수 로직, 외부 의존성 없음)

### 1. config.py (FR-01: 인증 및 설정 로드)

- [x] 1-1. `test_load_config_reads_api_id`: 환경변수에서 `TELEGRAM_API_ID`를 읽는다
- [x] 1-2. `test_load_config_reads_api_hash`: 환경변수에서 `TELEGRAM_API_HASH`를 읽는다
- [x] 1-3. `test_load_config_reads_phone`: 환경변수에서 `TELEGRAM_PHONE`을 읽는다
- [x] 1-4. `test_load_config_raises_on_missing_required`: 필수값 누락 시 에러 발생
- [x] 1-5. `test_load_config_reads_optional_with_defaults`: 선택값(`DOWNLOAD_MEDIA`, `LOG_LEVEL`, `DATA_DIR` 등)은 기본값 적용

### 2. logger.py (FR-10: 로깅)

- [x] 2-1. `test_log_format_matches_spec`: 로그 형식이 `{timestamp} [{level}] [{module}] {message}` 패턴과 일치
- [x] 2-2. `test_log_file_daily_rotation_name`: 로그 파일명이 `collector_{YYYY-MM-DD}.log` 형식
- [x] 2-3. `test_logger_outputs_to_console_and_file`: 콘솔과 파일에 동시 출력

### 3. metadata.py (FR-08: 메타데이터 관리)

- [x] 3-1. `test_load_returns_empty_when_file_missing`: 파일 없을 때 빈 dict 반환
- [x] 3-2. `test_save_writes_metadata_to_file`: 메타데이터를 JSON 파일로 저장
- [x] 3-3. `test_load_reads_saved_metadata`: 저장된 메타데이터를 올바르게 읽기
- [x] 3-4. `test_update_channel_metadata`: 특정 채널의 메타데이터만 업데이트
- [x] 3-5. `test_load_returns_empty_when_file_corrupted`: 파일 손상 시 빈 dict 반환 (초기화)
- [x] 3-6. `test_update_increments_total_collected`: `total_collected` 카운터 증가

### 4. message_parser.py (FR-05: 메시지 파싱)

- [x] 4-1. `test_parse_text_only_message`: 텍스트만 있는 메시지 파싱 → `message_id`, `text`, `has_media=False`
- [x] 4-2. `test_parse_message_with_none_text`: `text`가 None이면 빈 문자열 처리
- [x] 4-3. `test_parse_date_utc_iso8601`: `date` 필드가 UTC ISO8601 형식
- [x] 4-4. `test_parse_message_with_photo`: 사진 메시지 → `has_media=True`, `media_type="photo"`
- [x] 4-5. `test_parse_message_with_document`: 문서 메시지 → `media_type="document"`
- [x] 4-6. `test_parse_message_with_video`: 동영상 메시지 → `media_type="video"`
- [x] 4-7. `test_parse_message_with_caption`: 캡션 포함 미디어 → `text`에 캡션 저장
- [x] 4-8. `test_parse_message_views_and_forwards`: `views`, `forwards` 필드 추출
- [x] 4-9. `test_parse_edited_message`: 편집된 메시지 → `is_edit=True`, `edit_date` 설정
- [x] 4-10. `test_parse_message_collected_at_set`: `collected_at` 필드가 현재 시각으로 설정
- [x] 4-11. `test_parse_korean_text`: 한국어 텍스트가 정상 파싱

### 5. storage.py (FR-06: JSONL 파일 저장)

- [x] 5-1. `test_generate_file_path`: `channel_alias`와 `date`로 올바른 경로 생성 (`data/{alias}/{YYYY-MM-DD}.jsonl`)
- [x] 5-2. `test_creates_directory_if_not_exists`: 디렉토리 없으면 자동 생성
- [x] 5-3. `test_writes_single_message_as_jsonl`: 메시지 하나를 JSONL 한 줄로 저장
- [x] 5-4. `test_appends_to_existing_file`: 기존 파일에 append
- [x] 5-5. `test_preserves_korean_text_utf8`: 한국어 원문 보존 (`ensure_ascii=False`)
- [x] 5-6. `test_each_line_is_valid_json`: 각 줄이 유효한 JSON
- [x] 5-7. `test_skips_duplicate_message_id`: 동일 `message_id` 중복 저장 방지
- [x] 5-8. `test_retries_on_write_failure`: 쓰기 실패 시 최대 3회 재시도
- [x] 5-9. `test_logs_error_after_max_retries`: 재시도 초과 시 에러 로그

---

## Phase 2: 채널/연결 관리

### 6. channel_manager.py (FR-02: 채널 등록 및 관리)

- [x] 6-1. `test_parse_channels_from_json`: JSON 설정에서 채널 목록 파싱
- [x] 6-2. `test_filter_enabled_channels_only`: `enabled=true`인 채널만 필터링
- [x] 6-3. `test_channel_identified_by_username`: `username`으로 공개채널 식별
- [x] 6-4. `test_channel_identified_by_id`: `id`로 비공개채널 식별
- [x] 6-5. `test_channel_alias_assigned`: 채널별 별칭(alias) 지정
- [x] 6-6. `test_resolve_failure_logs_error_continues`: resolve 실패 시 에러 로그 + 나머지 채널 정상 등록

### 7. reconnect.py (FR-09: 재연결 및 백오프)

- [x] 7-1. `test_exponential_backoff_sequence`: 지수 백오프 계산 (30→60→120→240→300)
- [x] 7-2. `test_backoff_max_cap_300`: 최대 대기시간 300초 제한
- [x] 7-3. `test_backoff_resets_on_success`: 연결 성공 시 백오프 초기화
- [x] 7-4. `test_flood_wait_error_extracts_seconds`: `FloodWaitError`에서 대기시간 추출
- [x] 7-5. `test_reconnect_triggers_batch_collection`: 재연결 성공 시 배치 수집 1회 트리거

### 8. client.py (FR-01: 클라이언트 생성)

- [x] 8-1. `test_creates_client_with_correct_params`: `api_id`, `api_hash`로 TelegramClient 생성
- [x] 8-2. `test_session_file_in_session_directory`: 세션 파일 경로가 `session/` 디렉토리 내

---

## Phase 3: 수집 기능

### 9. media_downloader.py (FR-07: 미디어 다운로드)

- [x] 9-1. `test_generate_media_file_path`: 미디어 경로 생성 (`data/{alias}/media/{msg_id}_{filename}`)
- [x] 9-2. `test_skip_file_over_max_size`: 50MB 초과 파일 스킵 + 로그 기록
- [x] 9-3. `test_download_disabled_skips`: `DOWNLOAD_MEDIA=false` 시 다운로드 건너뜀
- [x] 9-4. `test_download_failure_does_not_affect_text_storage`: 다운로드 실패해도 텍스트 저장 정상 진행
- [x] 9-5. `test_downloads_highest_resolution_photo`: 사진 최고 해상도 다운로드

### 10. collector.py (FR-03: 실시간 메시지 수신)

- [x] 10-1. `test_handler_extracts_message_data`: 이벤트 핸들러가 메시지 데이터 추출
- [x] 10-2. `test_ignores_unregistered_channel`: 등록되지 않은 채널 메시지 무시
- [x] 10-3. `test_handles_edited_message_event`: `MessageEdited` 이벤트 처리
- [x] 10-4. `test_routes_message_to_parse_and_store`: 메시지 → 파서 → 스토리지 파이프라인 연동
- [x] 10-5. `test_handles_text_media_and_caption_messages`: 텍스트/미디어/캡션 모두 수신

### 11. batch_collector.py (FR-04: 배치 수집)

- [x] 11-1. `test_reads_last_message_id_from_metadata`: 메타데이터에서 `last_message_id` 읽기
- [x] 11-2. `test_builds_query_with_min_id`: `min_id` 파라미터로 조회 구성
- [x] 11-3. `test_limits_to_100_messages`: 한 번에 최대 100개 메시지 제한
- [x] 11-4. `test_skips_already_stored_messages`: 이미 저장된 메시지 중복 방지
- [x] 11-5. `test_updates_metadata_after_collection`: 수집 후 메타데이터 업데이트

---

## Phase 4: 통합 및 진입점

### 12. 통합 테스트

- [x] 12-1. `test_pipeline_receive_parse_store`: 수신 → 파싱 → 저장 전체 파이프라인
- [x] 12-2. `test_pipeline_with_media_download`: 미디어 다운로드 포함 파이프라인
- [x] 12-3. `test_batch_collection_pipeline`: 배치 수집 전체 흐름
- [x] 12-4. `test_duplicate_prevention_across_pipeline`: 파이프라인 전체에서 중복 방지

### 13. main.py / batch.py 진입점

- [x] 13-1. `test_main_registers_event_handlers`: main 실행 시 이벤트 핸들러 등록
- [x] 13-2. `test_main_connects_and_runs`: 클라이언트 연결 후 실행
- [x] 13-3. `test_batch_entry_runs_collection`: 배치 진입점 실행

---

## 작업 지침 (Agent 공통)

### 진행 절차

1. **작업 시작 전**: 이 파일(`plan.md`)을 읽고 다음 `[ ]` 항목을 확인한다.
2. **TDD 사이클 실행**:
   - **Red**: 해당 항목의 실패하는 테스트를 작성한다.
   - **Green**: 테스트를 통과하는 최소한의 코드를 구현한다.
   - **Refactor**: 필요 시 구조를 개선한다 (테스트 통과 유지).
3. **전체 테스트 실행**: `pytest tests/ -v` 로 기존 테스트 포함 전체 통과 확인.
4. **plan.md 업데이트**: 완료된 항목을 `[ ]` → `[x]`로 변경한다.
5. **다음 항목으로**: 위 과정을 반복한다.

### 상태 추적 규칙

- 각 테스트 항목 완료 즉시 `plan.md`를 업데이트하여 진행 상황을 기록한다.
- 이를 통해 작업이 중단되거나 다른 Agent가 이어받을 때 정확한 재개 지점을 알 수 있다.
- `[ ]` = 미완료 (다음 작업 대상), `[x]` = 완료
- 부분 완료(테스트만 작성, 구현 미완료 등)는 체크하지 않는다. 완전히 통과한 항목만 체크한다.

### 파일 위치 규칙

- 테스트 파일: `tests/test_{모듈명}.py`
- 소스 파일: `src/{모듈명}.py`
- 공용 fixture: `tests/conftest.py`
- 같은 모듈의 테스트는 하나의 테스트 파일에 누적 추가한다.

### 품질 규칙

- 매 단계마다 `pytest tests/ -v` 로 전체 테스트 통과 확인 (기존 테스트 깨지면 안 됨).
- 리팩토링이 필요하면 구조적 변경과 행위적 변경을 분리한다.
- 외부 API(Telethon)는 항상 모킹한다.
- 파일 I/O 테스트는 `tmp_path` fixture를 사용한다.
- Phase 0은 셋업이므로 테스트 없이 파일 생성 후 체크한다.

### 인수인계 지침

- 새 Agent가 작업을 이어받을 때: 이 파일에서 첫 번째 `[ ]` 항목을 찾아 그 항목부터 시작한다.
- 이전 Agent가 생성한 소스/테스트 파일을 반드시 읽고 기존 패턴을 따른다.
- `CLAUDE.md`의 TDD 원칙과 `PRD.md`의 요구사항을 함께 참조한다.

# OpenClaw Docker 운영 가이드

이 프로젝트는 OpenClaw Docker 환경(예: `~/.openclaw/workspace/<project>`)에서도 실행/로그확인/채널관리가 가능하도록 업데이트되었습니다.

## 0) 빠른 시작 (권장)

`scripts/openclaw.sh` 하나로 실행/로그/채널/테스트를 처리합니다.

```bash
cd /home/ubuntu/.openclaw/workspace/telegram_scrap
chmod +x scripts/openclaw.sh

# 환경 확인
./scripts/openclaw.sh env

# 실시간 실행
./scripts/openclaw.sh run realtime

# 배치 실행
./scripts/openclaw.sh run batch

# 로그 목록/최근 로그
./scripts/openclaw.sh logs list
./scripts/openclaw.sh logs tail --lines 100

# 채널 조회/비활성
./scripts/openclaw.sh channel list
./scripts/openclaw.sh channel disable --alias invest_a

# 테스트 (tmp_path 권한 우회 포함)
./scripts/openclaw.sh test -q
```

## 1) 워크스페이스 기준 실행

상대 경로(`channels.json`, `data/`, `logs/`, `session/`)는 기본적으로 현재 작업 디렉터리 기준으로 해석됩니다.
원하는 루트를 강제하려면 `--workspace` 또는 `TICC_WORKSPACE_DIR`를 사용하세요.

```bash
python -m src.run --mode realtime --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap
python -m src.run --mode batch --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap
```

## 2) 로그 확인

`src.log_cli`로 로그 파일 목록/최근 로그를 확인할 수 있습니다.

```bash
python -m src.log_cli --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap list
python -m src.log_cli --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap tail --lines 100
python -m src.log_cli --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap tail --file collector_2026-03-09.log --lines 200
```

## 3) 채널 관리

`src.channel_cli`가 `add/list/enable/disable/remove`를 지원합니다.

```bash
python -m src.channel_cli add --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap --alias invest_a --username investnews_kr
python -m src.channel_cli list --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap
python -m src.channel_cli disable --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap --alias invest_a
python -m src.channel_cli enable --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap --alias invest_a
python -m src.channel_cli remove --workspace /home/ubuntu/.openclaw/workspace/telegram_scrap --alias invest_a
```

## 4) 테스트 권한 이슈 회피

OpenClaw 컨테이너에서 시스템 temp 권한 문제가 있으면 아래처럼 워크스페이스 내부를 temp로 고정하세요.

```bash
mkdir -p tests/.tmp
TMPDIR=$PWD/tests/.tmp TEMP=$PWD/tests/.tmp TMP=$PWD/tests/.tmp \
  python -m pytest tests/ --basetemp "$PWD/tests/.tmp/pytest" -q
```

`scripts/openclaw.sh test`는 위 설정을 자동으로 적용합니다.

## 5) 권장 환경 변수

```bash
export TICC_WORKSPACE_DIR=/home/ubuntu/.openclaw/workspace/telegram_scrap
export DATA_DIR=data
export LOG_DIR=logs
export SESSION_DIR=session
```

환경 변수를 설정해두면 매번 `--workspace`를 주지 않아도 동일 동작합니다.

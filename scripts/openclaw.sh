#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DEFAULT="${TICC_WORKSPACE_DIR:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace/telegram_scrap}}"
WORKSPACE="${WORKSPACE:-$WORKSPACE_DEFAULT}"

print_usage() {
  cat <<'USAGE'
Usage:
  scripts/openclaw.sh run [realtime|batch] [extra args...]
  scripts/openclaw.sh logs [list|tail] [extra args...]
  scripts/openclaw.sh channel [add|list|enable|disable|remove] [args...]
  scripts/openclaw.sh test [pytest args...]
  scripts/openclaw.sh env

Notes:
  - WORKSPACE can be overridden by env WORKSPACE.
  - Default workspace: $TICC_WORKSPACE_DIR or $OPENCLAW_WORKSPACE or ~/.openclaw/workspace/telegram_scrap
USAGE
}

run_mode() {
  local mode="${1:-realtime}"
  shift || true
  python -m src.run --mode "$mode" --workspace "$WORKSPACE" "$@"
}

logs_mode() {
  local cmd="${1:-list}"
  shift || true
  python -m src.log_cli --workspace "$WORKSPACE" "$cmd" "$@"
}

channel_mode() {
  local cmd="${1:-list}"
  shift || true
  python -m src.channel_cli "$cmd" --workspace "$WORKSPACE" "$@"
}

test_mode() {
  local base_temp="$WORKSPACE/tests/.tmp/pytest"
  mkdir -p "$base_temp"

  export TMPDIR="$WORKSPACE/tests/.tmp"
  export TEMP="$WORKSPACE/tests/.tmp"
  export TMP="$WORKSPACE/tests/.tmp"

  python -m pytest tests/ --basetemp "$base_temp" "$@"
}

show_env() {
  cat <<EOF
WORKSPACE=$WORKSPACE
TICC_WORKSPACE_DIR=${TICC_WORKSPACE_DIR:-}
OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE:-}
TMPDIR=${TMPDIR:-}
EOF
}

main() {
  local area="${1:-}"
  if [[ -z "$area" ]]; then
    print_usage
    exit 1
  fi
  shift

  case "$area" in
    run)
      run_mode "$@"
      ;;
    logs)
      logs_mode "$@"
      ;;
    channel)
      channel_mode "$@"
      ;;
    test)
      test_mode "$@"
      ;;
    env)
      show_env
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
}

main "$@"

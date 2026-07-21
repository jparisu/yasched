#!/usr/bin/env bash
# =============================================================================
# Run yasched locally against your personal agenda. Designed as a daily driver:
# after the first run it starts in ~1s, fully offline, on a stable URL.
#
#   ./run.sh                     # serve in the FOREGROUND (Ctrl-C to stop)
#   ./run.sh --daemon            # serve in the BACKGROUND, print URL, return
#   ./run.sh --stop              # stop the background server
#   ./run.sh --restart           # restart it in the background
#   ./run.sh --status            # is it running?
#   ./run.sh --logs              # follow the background server's log
#
#   ./run.sh path/to.yaml        # a specific agenda file
#   ./run.sh --daemon --open     # background + open browser
#   ./run.sh --reinstall         # after changing dependencies
#   ./run.sh --rebuild           # after changing the frontend (apps/web)
#   HOST=0.0.0.0 PORT=9000 ./run.sh --daemon
#
# Python code changes are picked up on the next run (editable install). The
# background server survives closing the terminal. PID/log live under
# ~/.yasched/ and are keyed by port, so --stop/--status use the same PORT.
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

REINSTALL=0
REBUILD=0
OPEN=0
DAEMON=0
ACTION="start"
AGENDA_ARG=""
for arg in "$@"; do
  case "$arg" in
    -d | --daemon) DAEMON=1 ;;
    --stop) ACTION="stop" ;;
    --status) ACTION="status" ;;
    --restart) ACTION="restart"; DAEMON=1 ;;
    --logs) ACTION="logs" ;;
    --reinstall) REINSTALL=1 ;;
    --rebuild) REBUILD=1 ;;
    --open) OPEN=1 ;;
    --*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *) AGENDA_ARG="$arg" ;;
  esac
done

VENV="${VENV:-.venv}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
PYTHON="${PYTHON:-python3}"
VENV_BIN="$VENV/bin"
AGENDA="${AGENDA_ARG:-${YASCHED_AGENDA:-$HOME/.yasched/agenda.yaml}}"
export YASCHED_AGENDA="$AGENDA"

STATE_DIR="${YASCHED_STATE_DIR:-$HOME/.yasched}"
PIDFILE="$STATE_DIR/run-$PORT.pid"
LOG="$STATE_DIR/run-$PORT.log"
AGENDAFILE="$STATE_DIR/run-$PORT.agenda"
mkdir -p "$STATE_DIR"

DISPLAY_HOST="$HOST"
[ "$HOST" = "0.0.0.0" ] && DISPLAY_HOST="127.0.0.1"
URL="http://$DISPLAY_HOST:$PORT/"

is_running() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null
}

do_stop() {
  if is_running; then
    pid="$(cat "$PIDFILE")"
    echo "▶ stopping yasched (pid $pid, port $PORT)"
    kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 25); do is_running || break; sleep 0.2; done
    if is_running; then kill -9 "$pid" 2>/dev/null || true; fi
    rm -f "$PIDFILE" "$AGENDAFILE"
    echo "  stopped."
  else
    echo "yasched is not running on port $PORT."
    rm -f "$PIDFILE" "$AGENDAFILE"
  fi
}

# --- control-only actions (no install/build) -------------------------------
case "$ACTION" in
  stop)
    do_stop
    exit 0
    ;;
  status)
    if is_running; then
      running_agenda="$AGENDA"
      [ -f "$AGENDAFILE" ] && running_agenda="$(cat "$AGENDAFILE")"
      echo "yasched is running — pid $(cat "$PIDFILE"), $URL (agenda: $running_agenda)"
    else
      echo "yasched is not running on port $PORT."
    fi
    exit 0
    ;;
  logs)
    [ -f "$LOG" ] || { echo "no log at $LOG (start with --daemon first)"; exit 1; }
    exec tail -n 100 -f "$LOG"
    ;;
esac

[ "$ACTION" = "restart" ] && do_stop

# --- ensure environment (only when needed) ---------------------------------
if [ ! -x "$VENV_BIN/python" ]; then
  echo "▶ creating virtualenv ($VENV)"
  "$PYTHON" -m venv "$VENV"
  REINSTALL=1
fi
if [ ! -x "$VENV_BIN/yasched" ] || [ "$REINSTALL" = 1 ]; then
  echo "▶ installing yasched (editable)"
  "$VENV_BIN/python" -m pip install -e .
fi
if [ ! -f apps/web/dist/index.html ] || [ "$REBUILD" = 1 ]; then
  echo "▶ building frontend"
  ( cd apps/web && npm install && npm run build )
fi
if [ ! -f "$AGENDA" ]; then
  echo "▶ creating a starter agenda at $AGENDA"
  "$VENV_BIN/yasched" init --agenda "$AGENDA"
fi

if [ "$OPEN" = 1 ] && command -v xdg-open >/dev/null 2>&1; then
  ( sleep 1; xdg-open "$URL" >/dev/null 2>&1 || true ) &
fi

# --- background (daemon) ----------------------------------------------------
if [ "$DAEMON" = 1 ]; then
  if is_running; then
    echo "yasched is already running — pid $(cat "$PIDFILE"), $URL. Use --restart or --stop."
    exit 0
  fi
  nohup "$VENV_BIN/yasched" serve --agenda "$AGENDA" --host "$HOST" --port "$PORT" \
    >"$LOG" 2>&1 </dev/null &
  echo $! >"$PIDFILE"
  echo "$AGENDA" >"$AGENDAFILE"
  disown 2>/dev/null || true
  sleep 0.5
  if ! is_running; then
    echo "▶ failed to start — last log lines:" >&2
    tail -n 15 "$LOG" >&2 || true
    rm -f "$PIDFILE"
    exit 1
  fi
  echo "▶ yasched running in background at  $URL"
  echo "  pid $(cat "$PIDFILE")  ·  agenda: $AGENDA"
  echo "  logs: $LOG    stop: PORT=$PORT $(basename "$0") --stop"
  exit 0
fi

# --- foreground -------------------------------------------------------------
echo "▶ yasched is at  $URL   (agenda: $AGENDA, Ctrl-C to stop)"
exec "$VENV_BIN/yasched" serve --agenda "$AGENDA" --host "$HOST" --port "$PORT"

#!/usr/bin/env bash
# Bounded continuation run (SPEC §35, §39): repeats scheduler ticks without a manual "continue" until
# (a) no eligible work remains, (b) budget pause, (c) blocked on credentials, or (d) the iteration ceiling.
# Uses a flock so two runs cannot overlap on the same host; every iteration checkpoints to the DB (jobs/runs/heartbeats).
# Usage: scripts/continuation_demo.sh [max_iterations] [--seed-demo]
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; MAX="${1:-6}"; LOG="$ROOT/build/continuation.log"; LOCK="$ROOT/build/continuation.lock"
mkdir -p "$ROOT/build"
exec 9>"$LOCK"; flock -n 9 || { echo "another continuation run holds $LOCK; exiting" | tee -a "$LOG"; exit 11; }
cd "$ROOT/worker"
if [ "${2:-}" = "--seed-demo" ]; then
  python - <<'PY'
from campus_worker.db import connect
from campus_worker import queue as q
from campus_worker.types import JobRecord
conn = connect()
a, ca = q.enqueue(conn, JobRecord(job_type="noop", idempotency_key="demo:collect-rates:v1", payload={"step": "collect rates page (demo)"}))
b, cb = q.enqueue(conn, JobRecord(job_type="fail_once_then_succeed", idempotency_key="demo:extract-claims:v1", payload={"step": "extract claims (demo, flaky once)"}, depends_on=[a]))
c, cc = q.enqueue(conn, JobRecord(job_type="noop", idempotency_key="demo:build-brief:v1", payload={"step": "build brief (demo)"}, depends_on=[b]))
print(f"seeded dependent chain a={a} b={b} c={c} created={ca},{cb},{cc}")
PY
fi
echo "=== continuation run $(date -u +%FT%TZ) max_iterations=$MAX ===" | tee -a "$LOG"
for i in $(seq 1 "$MAX"); do
  out="$(python -m campus_worker.cli run-once 2>&1)"; code=$?
  status="$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["status"], "ran=" + ",".join(r["job_type"]+":"+r["result"] for r in d["ran"]))' 2>/dev/null || echo "parse_error")"
  echo "iteration $i: exit=$code $status" | tee -a "$LOG"
  case $code in
    10) # waiting: nothing eligible now — but retry_wait jobs may become eligible; peek
        pending="$(python -c 'from campus_worker.db import connect; from campus_worker import queue as q; print(q.counts(connect()).get("retry_wait",0))')"
        if [ "$pending" -gt 0 ]; then echo "iteration $i: $pending job(s) in retry_wait; advancing not_before for demo and continuing" | tee -a "$LOG"; python -c 'from campus_worker.db import connect; c=connect(); c.execute("UPDATE jobs SET not_before=now() WHERE state=%s", ("retry_wait",)); c.commit()'; continue; fi
        echo "STOP: no unblocked work remains (exit 10)" | tee -a "$LOG"; exit 0;;
    20) echo "STOP: usage paused by budget cap (exit 20)" | tee -a "$LOG"; exit 20;;
    30) echo "STOP: blocked on credentials (exit 30)" | tee -a "$LOG"; exit 30;;
    0)  ;;
    *)  echo "STOP: tick failed (exit $code)" | tee -a "$LOG"; exit 1;;
  esac
done
echo "STOP: iteration ceiling $MAX reached" | tee -a "$LOG"; exit 12

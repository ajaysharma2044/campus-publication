#!/usr/bin/env bash
# Fixture stand-ins for one `claude -p --output-format json` iteration (AT3–AT7 loop tests). No model, no network.
# Usage: iteration_stub.sh ok|nowork|fail|usage|auth|slow   (CAMPUS_STUB_SEQUENCE="ok,ok,nowork" picks by $CAMPUS_ITERATION)
mode="${1:-ok}"
if [ -n "${CAMPUS_STUB_SEQUENCE:-}" ]; then
  i="${CAMPUS_ITERATION:-1}"; mode="$(printf '%s' "$CAMPUS_STUB_SEQUENCE" | tr ',' '\n' | sed -n "${i}p")"; [ -n "$mode" ] || mode="nowork"
fi
if [ -n "${CAMPUS_STUB_MARK_FILE:-}" ]; then echo "$(date -u +%FT%TZ) iteration=${CAMPUS_ITERATION:-?} mode=$mode" >> "$CAMPUS_STUB_MARK_FILE"; fi
summary() { printf '{"iteration_summary": {"task_id": "%s", "lane": "%s", "result": "%s", "agents": %s, "checks": %s, "commit": "%s", "notes": "%s"}}' "$@"; }
case "$mode" in
  ok)
    body="$(summary "FIX-001" "maintenance" "succeeded" '["analyst"]' '[{"name":"pytest","pass":true}]' "stub" "fixture iteration")"
    printf '{"type":"result","subtype":"success","is_error":false,"num_turns":4,"duration_ms":1200,"total_cost_usd":0,"session_id":"stub","result":"Work done.\\n%s"}\n' "$(printf '%s' "$body" | sed 's/"/\\"/g')"; exit 0;;
  nowork)
    body="$(summary "" "none" "no_work" '[]' '[{"name":"pytest","pass":true}]' "stub" "nothing unblocked")"
    printf '{"type":"result","subtype":"success","is_error":false,"num_turns":2,"duration_ms":800,"total_cost_usd":0,"session_id":"stub","result":"No unblocked work remains.\\n%s"}\n' "$(printf '%s' "$body" | sed 's/"/\\"/g')"; exit 0;;
  slow)
    sleep "${CAMPUS_STUB_SLEEP:-3}"
    body="$(summary "FIX-002" "maintenance" "succeeded" '["analyst"]' '[{"name":"pytest","pass":true}]' "stub" "slow fixture iteration")"
    printf '{"type":"result","subtype":"success","is_error":false,"num_turns":3,"duration_ms":3000,"total_cost_usd":0,"session_id":"stub","result":"Done.\\n%s"}\n' "$(printf '%s' "$body" | sed 's/"/\\"/g')"; exit 0;;
  fail)
    printf '{"type":"result","subtype":"error_during_execution","is_error":true,"num_turns":1,"duration_ms":300,"total_cost_usd":0,"session_id":"stub","result":"Error: fixture failure (forced)"}\n'; exit 1;;
  usage)
    printf '{"type":"result","subtype":"success","is_error":true,"num_turns":1,"duration_ms":100,"total_cost_usd":0,"session_id":"stub","result":"You have hit your usage limit. Your limit will reset at 3pm (America/Los_Angeles)."}\n'; exit 1;;
  auth)
    printf '{"type":"result","subtype":"success","is_error":true,"num_turns":1,"duration_ms":90,"total_cost_usd":0,"session_id":"stub","result":"Not logged in · Please run /login"}\n'; exit 1;;
  *) echo "unknown stub mode $mode" >&2; exit 2;;
esac

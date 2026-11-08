#!/usr/bin/env bash
# Stop any running v2 step cleanly: workers finish the sessions in flight and start nothing new.
# The next step run removes the file on its own.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$ROOT/.run" && touch "$ROOT/.run/STOP"
echo "STOP requested ($ROOT/.run/STOP): sessions in flight finish, nothing new starts"

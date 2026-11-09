#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)";tmp="$(mktemp -d)";trap 'rm -rf "$tmp"' EXIT
python -m pip wheel --no-deps --wheel-dir "$tmp/dist" "$root" > "$tmp/build.log"
python -m venv "$tmp/env"
"$tmp/env/bin/python" -m pip install --no-deps "$tmp"/dist/*.whl > "$tmp/install.log"
cd "$tmp"
"$tmp/env/bin/python" -I "$root/tools/verify_installed.py" "$root"
"$tmp/env/bin/submodlab" --spec "$root/examples/coverage.json" --json cli.json
"$tmp/env/bin/python" -I - "$root" <<'PY'
import json,sys
from pathlib import Path
from submodlab import audit
r=Path(sys.argv[1]);assert json.load(open('cli.json'))==audit(json.load(open(r/'examples/coverage.json')))
assert json.load(open('cli.json'))['greedy_value']=='5'
print('Installed console CLI, greedy and optimum witnesses, all 24 reports and four module origins passed')
PY
"$tmp/env/bin/python" -I "$root/tools/verify_rounding_installed.py" "$root"
"$tmp/env/bin/python" -I -m submodlab.rounding_cli --spec "$root/examples/rounding.json" --json rounding.json
"$tmp/env/bin/python" -I - "$root" <<'PY'
import json,sys
from pathlib import Path
from submodlab.rounding import rounding_audit
r=Path(sys.argv[1]);assert json.load(open('rounding.json'))==rounding_audit(json.load(open(r/'examples/rounding.json')))
print('Installed rounding module CLI, all 21 reports and six module origins passed')
PY

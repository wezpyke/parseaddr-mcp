#!/usr/bin/env bash
# Publish the `parseaddr` client to npm and PyPI in one step.
#
#   NPM_TOKEN=npm_... PYPI_TOKEN=pypi-... scripts/publish.sh
#
# NPM_TOKEN: npmjs.com > Access Tokens > Granular, "Read and write", packages: all (the first
#            publish of a new name needs all; narrow it to `parseaddr` afterwards).
# PYPI_TOKEN: pypi.org > Account settings > API tokens, scope "Entire account" for the first
#            upload (the project does not exist yet); swap for a project-scoped token after.
# Either token may be left out to publish only the other registry.
# DRY_RUN=1 runs every step but the upload (npm publish --dry-run, no twine upload).
#
# Order: check versions, run BOTH test suites and build, and only then upload anything.
# No GitHub Actions on purpose: Actions minutes are off for this portfolio.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -n "${NPM_TOKEN:-}${PYPI_TOKEN:-}" ] || { echo "Set NPM_TOKEN and/or PYPI_TOKEN." >&2; exit 1; }

NPM_VER=$(node -p 'require("./packages/npm/package.json").version')
PY_VER=$(sed -n 's/^version = "\(.*\)"/\1/p' packages/pypi/pyproject.toml)
JS_CONST=$(sed -n 's/^export const VERSION = "\(.*\)";/\1/p' packages/npm/index.js)
PY_CONST=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' packages/pypi/parseaddr/__init__.py)
[ "$NPM_VER" = "$JS_CONST" ] || { echo "package.json $NPM_VER != index.js VERSION $JS_CONST" >&2; exit 1; }
[ "$PY_VER" = "$PY_CONST" ] || { echo "pyproject $PY_VER != __version__ $PY_CONST" >&2; exit 1; }

live() { [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = 200 ]; }
if [ -n "${NPM_TOKEN:-}" ] && live "https://registry.npmjs.org/parseaddr/$NPM_VER"; then
  echo "npm parseaddr@$NPM_VER is already published; bump the version." >&2; exit 1
fi
if [ -n "${PYPI_TOKEN:-}" ] && live "https://pypi.org/pypi/parseaddr/$PY_VER/json"; then
  echo "PyPI parseaddr $PY_VER is already published; bump the version." >&2; exit 1
fi

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT

# 1. Test and build both packages. Nothing is uploaded unless all of this passes.
(cd packages/npm && npm install --no-audit --no-fund --silent && npm test)
python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install -q build twine pytest -e "packages/pypi[mcp]"
(cd packages/pypi && "$WORK/venv/bin/pytest" -q)
"$WORK/venv/bin/python" -m build -q --outdir "$WORK/dist" packages/pypi
"$WORK/venv/bin/twine" check "$WORK/dist/"*

# 2. Upload. Tokens go to a temp npmrc / env var and are never echoed.
if [ -n "${NPM_TOKEN:-}" ]; then
  printf '//registry.npmjs.org/:_authToken=%s\n' "$NPM_TOKEN" > "$WORK/.npmrc"
  (cd packages/npm && NPM_CONFIG_USERCONFIG="$WORK/.npmrc" npm publish --access public ${DRY_RUN:+--dry-run})
  [ -n "${DRY_RUN:-}" ] || echo "npm: https://www.npmjs.com/package/parseaddr/v/$NPM_VER"
fi
if [ -n "${PYPI_TOKEN:-}" ]; then
  if [ -n "${DRY_RUN:-}" ]; then
    echo "DRY_RUN: skipping twine upload"
  else
    TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" "$WORK/venv/bin/twine" upload "$WORK/dist/"*
    echo "PyPI: https://pypi.org/project/parseaddr/$PY_VER/"
  fi
fi

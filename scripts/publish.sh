#!/usr/bin/env bash
# Publish the `parseaddr` client to npm and PyPI in one step.
#
#   NPM_TOKEN=npm_... PYPI_TOKEN=pypi-... scripts/publish.sh
#
# NPM_TOKEN: npmjs.com > Access Tokens > Granular, "Read and write", packages: all (first
#            publish of a new name needs all; narrow it to `parseaddr` afterwards).
# PYPI_TOKEN: pypi.org > Account settings > API tokens, scope "Entire account" for the first
#            upload (the project does not exist yet); swap for a project-scoped token after.
# Either token may be left out to publish only the other registry.
# DRY_RUN=1 runs every step but the upload (npm publish --dry-run, no twine upload).
#
# Runs both test suites first and refuses to publish a version that is already live.
# No GitHub Actions on purpose: Actions minutes are off for this portfolio.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD

[ -n "${NPM_TOKEN:-}${PYPI_TOKEN:-}" ] || { echo "Set NPM_TOKEN and/or PYPI_TOKEN." >&2; exit 1; }

NPM_VER=$(node -p 'require("./packages/npm/package.json").version')
PY_VER=$(sed -n 's/^version = "\(.*\)"/\1/p' packages/pypi/pyproject.toml)
JS_CONST=$(sed -n 's/^export const VERSION = "\(.*\)";/\1/p' packages/npm/index.js)
PY_CONST=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' packages/pypi/parseaddr/__init__.py)
[ "$NPM_VER" = "$JS_CONST" ] || { echo "package.json $NPM_VER != index.js VERSION $JS_CONST" >&2; exit 1; }
[ "$PY_VER" = "$PY_CONST" ] || { echo "pyproject $PY_VER != __version__ $PY_CONST" >&2; exit 1; }

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT

if [ -n "${NPM_TOKEN:-}" ]; then
  if [ "$(curl -s -o /dev/null -w '%{http_code}' "https://registry.npmjs.org/parseaddr/$NPM_VER")" = 200 ]; then
    echo "npm parseaddr@$NPM_VER is already published; bump the version." >&2; exit 1
  fi
  (cd packages/npm && npm install --no-audit --no-fund --silent && npm test)
  printf '//registry.npmjs.org/:_authToken=%s\n' "$NPM_TOKEN" > "$WORK/.npmrc"
  (cd packages/npm && NPM_CONFIG_USERCONFIG="$WORK/.npmrc" npm publish --access public ${DRY_RUN:+--dry-run})
  [ -n "${DRY_RUN:-}" ] || echo "npm: https://www.npmjs.com/package/parseaddr/v/$NPM_VER"
fi

if [ -n "${PYPI_TOKEN:-}" ]; then
  if [ "$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/parseaddr/$PY_VER/json")" = 200 ]; then
    echo "PyPI parseaddr $PY_VER is already published; bump the version." >&2; exit 1
  fi
  python3 -m venv "$WORK/venv"
  "$WORK/venv/bin/pip" install -q build twine pytest -e "packages/pypi[mcp]"
  (cd packages/pypi && "$WORK/venv/bin/pytest" -q)
  "$WORK/venv/bin/python" -m build -q --outdir "$WORK/dist" packages/pypi
  "$WORK/venv/bin/twine" check "$WORK/dist/"*
  [ -n "${DRY_RUN:-}" ] && { echo "DRY_RUN: skipping twine upload"; exit 0; }
  TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" "$WORK/venv/bin/twine" upload "$WORK/dist/"*
  echo "PyPI: https://pypi.org/project/parseaddr/$PY_VER/"
fi

#!/usr/bin/env bash
set -euo pipefail

TASK_DIR=$(cd -- "$(dirname -- "$0")"/.. && pwd)
OUT_DIR="$TASK_DIR/tinygo-wasm/dist"
mkdir -p "$OUT_DIR"

TINYGO_BIN=${TINYGO_BIN:-tinygo}

"$TINYGO_BIN" version 1>&2
"$TINYGO_BIN" build -target wasm -o "$OUT_DIR/tinygo.wasm" "$TASK_DIR/tinygo-wasm"

TINYGO_ROOT=$(cd -- "$(dirname -- "$TINYGO_BIN")"/.. && pwd)
cp "$TINYGO_ROOT/lib/wasm_exec.js" "$OUT_DIR/wasm_exec.js"

echo "Built TinyGo artifacts in $OUT_DIR" 1>&2

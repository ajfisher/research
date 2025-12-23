#!/usr/bin/env bash
set -euo pipefail

# Build a WebAssembly module using the standard Go toolchain.
TASK_DIR=$(cd -- "$(dirname -- "$0")"/.. && pwd)
OUT_DIR="$TASK_DIR/native-go-wasm/dist"
mkdir -p "$OUT_DIR"

GOOS=js GOARCH=wasm go build -o "$OUT_DIR/native-go.wasm" "$TASK_DIR/native-go-wasm"

# Locate wasm_exec.js (its location differs between Go distributions).
WASM_EXEC_PATH="$(go env GOROOT)/misc/wasm/wasm_exec.js"
if [[ ! -f "$WASM_EXEC_PATH" ]]; then
  WASM_EXEC_PATH="$(go env GOROOT)/lib/wasm/wasm_exec.js"
fi
cp "$WASM_EXEC_PATH" "$OUT_DIR/"
cp "$TASK_DIR/native-go-wasm/index.html" "$OUT_DIR/"

echo "Built artifacts in $OUT_DIR" 1>&2

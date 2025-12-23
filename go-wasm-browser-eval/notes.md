## 2025-02-03 00:00 UTC - Initial setup
- Created research task directory structure for evaluating Go WebAssembly options in the browser.
- Goal: compare native Go WebAssembly support vs. alternatives (e.g., TinyGo) with small experiments.

## 2025-02-03 00:20 UTC - Created native Go WASM sample
- Added native Go WASM example exposing CSV summary and uppercase helpers via syscall/js.
- Created build script that compiles with GOOS=js GOARCH=wasm and copies wasm_exec.js to dist/.
- Added simple HTML harness to call the exported functions in the browser.

## 2025-02-03 00:45 UTC - Build iteration
- Encountered missing wasm_exec.js under GOROOT/misc; discovered it lives under lib/wasm in this toolchain.
- Updated build script to detect either location before copying.
- Verified native Go WASM build by compiling main.go (produced ~2.5MB wasm locally).

## 2025-02-03 01:05 UTC - Native WASM test
- Built the sample using the helper script; wasm_exec.js located automatically.
- Verified functionality via Node harness calling exported functions (uppercase + CSV summary).

## 2025-02-03 01:35 UTC - TinyGo attempt
- Downloaded TinyGo 0.32.0 and 0.30.0 release tarballs plus Go 1.22.10 toolchain for compatibility testing.
- `tinygo` binary reports it was built with Go 1.24.3 and aborts: "requires go version 1.19 through 1.22, got go1.24" even when GOROOT/PATH point at Go 1.22.
- Conclusion: current prebuilt TinyGo artifacts in this environment are not usable without building TinyGo against a supported Go toolchain.

## 2025-02-03 01:45 UTC - Artifact sizing
- Native Go WASM artifact size: 2.5M (from `code/native-go-wasm/dist/native-go.wasm`).
- Expect TinyGo output would be substantially smaller based on docs, but compilation is currently blocked by toolchain version mismatch.

## 2025-02-03 01:55 UTC - Build ergonomics
- Updated native build script to copy the HTML harness into `dist/` so the demo can be served directly after building.

## 2025-02-03 02:05 UTC - Browser harness screenshot attempt
- Served the native demo via `python -m http.server` from `code/native-go-wasm/dist` and tried capturing a Playwright screenshot; the browser container reported a 404 (port-forwarding issue), so no screenshot was saved in the repo.

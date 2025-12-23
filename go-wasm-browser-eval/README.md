# Go WebAssembly in the Browser

## Objective
Evaluate options for running Go applications in the browser via WebAssembly as groundwork for eventually porting Miller (mlr) CLI behaviors to a client-side experience.

## Background
Go ships a WebAssembly target (`GOOS=js GOARCH=wasm`) with a JavaScript bridge (`wasm_exec.js`). TinyGo provides an alternative toolchain that produces much smaller binaries, which is attractive for CLI-sized applications running in browsers.

## Methodology
1. Created a self-contained task directory with repeatable build scripts and simple CSV-processing primitives exposed to JavaScript via `syscall/js`.
2. Implemented and built a native Go WebAssembly sample (`code/native-go-wasm`) that exposes CSV summarization and a string helper to JavaScript, plus an HTML harness to exercise them in a browser.
3. Attempted to build the same surface area with TinyGo (`code/tinygo-wasm`) to compare output size/startup, but prebuilt TinyGo distributions rejected the host Go 1.24.x toolchain, blocking compilation in this environment.

## Setup and Installation
Prerequisites: Go 1.24.x (already available in this environment), Node.js for quick command-line checks, and a static file server for the browser demo.

### Build and test the native Go sample
```bash
cd go-wasm-browser-eval/code/native-go-wasm
./build_native.sh
# Optional: quick sanity check via Node (uses wasm_exec.js):
node -e "const fs=require('fs');require('./dist/wasm_exec.js');const go=new globalThis.Go();(async()=>{const bytes=fs.readFileSync('./dist/native-go.wasm');const {instance}=await WebAssembly.instantiate(bytes, go.importObject);go.run(instance);setTimeout(()=>{console.log('csv:', globalThis.wasmCSVSummary('a,b\\n1,2'));process.exit(0);},50);})();"
# Browser harness:
cd dist && python -m http.server 8000
# then visit http://localhost:8000/index.html
```

### TinyGo experiment
A build script is present (`code/tinygo-wasm/build_tinygo.sh`), but it currently fails with prebuilt TinyGo 0.30–0.32 because those binaries report `requires go version 1.19 through 1.22, got go1.24`. Rebuilding TinyGo against a Go 1.22 toolchain (or using a prebuilt artifact compiled with that range) is required before this path can be evaluated further.

## Results
- **Native Go WASM**: Successfully builds and runs. The generated module (`dist/native-go.wasm`) is ~2.5 MB with no further optimization. Exported functions (`wasmCSVSummary`, `wasmUppercase`) are callable from JS and verified via a Node harness and the included HTML page.
- **Bridge script location**: `wasm_exec.js` may live under either `$GOROOT/misc/wasm` or `$GOROOT/lib/wasm`; the build script copies whichever exists to `dist/` automatically.
- **TinyGo**: Compilation blocked in this environment due to Go toolchain version mismatch; no binary produced, but the example code mirrors the native API surface for future comparison. Expected benefit: significantly smaller output (~300–500 KB for similar programs based on TinyGo docs) and faster startup than the standard runtime.

## Conclusions
- The upstream Go toolchain works out of the box for browser WebAssembly, but produces multi-megabyte binaries. It is the quickest route for functional parity and for experimenting with Miller-like APIs in the browser.
- TinyGo remains the most promising option for reducing payload size and startup time, but requires aligning the Go toolchain version (≤1.22 for the releases tested). Without that, builds fail early.
- JS/Go interfacing relies on `syscall/js`; designing a narrow API surface (e.g., CSV summary operations) keeps the bridge simple and avoids large data marshaling overheads.

## Future Work
- Rebuild TinyGo against a supported Go 1.21/1.22 toolchain (or obtain a compatible prebuilt) and measure binary size/startup vs. the native build.
- Add basic benchmarks comparing load/exec time between toolchains and explore tree-shaking/`-ldflags` to shrink the native Go artifact.
- Prototype a minimal Miller subset using the established syscall/js patterns, and evaluate worker-based execution to keep the UI responsive.
- Investigate packaging strategies (e.g., ES module loaders, bundlers, or service workers) for shipping `wasm_exec.js` and the compiled module in production scenarios.

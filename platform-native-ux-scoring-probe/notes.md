## 2025-02-21 00:00 UTC - Project setup
- Created project folder `platform-native-ux-scoring-probe` with research structure.
- Planning to build Playwright-based CLI to score browser-native UX.

## 2025-02-21 00:20 UTC - Implemented CLI scaffold
- Initialized Node/TypeScript project under `code/` with Playwright, YAML parsing, and scoring logic.
- Added DOM metric collector, scoring heuristics, and flow runner with no-JS replay.
- Created sample flows config covering ajfisher.me and beyondblue.org.au paths.

## 2025-02-21 00:35 UTC - Documentation and checks
- Wrote project README with objective, workflow, and run instructions.
- Ran `npm run lint` (tsc --noEmit) to validate TypeScript wiring.

## 2025-02-21 01:10 UTC - Example flow execution
- Installed Playwright browser dependencies and enabled HTTPS ignoring in contexts to handle self-signed certs.
- Ran example flows against ajfisher.me and beyondblue.org.au, generating `results/reports/report.json` with scores and raw metrics.

## 2025-02-21 02:00 UTC - Step-level metrics
- Extended flow runner to record DOM/network metrics per step and include them in the report output alongside aggregated totals.
- Re-ran the sample flows to capture richer per-step data in `results/reports/report.json`.

## 2025-02-21 03:00 UTC - HTML report and broader sample sites
- Added optional HTML report generation driven by the JSON output, with score explanations and weighted platform-native totals.
- Enabled per-flow base URLs and refreshed the sample flows to cover Amazon, Wikipedia, and Mozilla (removing the Beyond Blue flow).
- Ran the updated flows to regenerate JSON and HTML sample reports under `results/reports/`.

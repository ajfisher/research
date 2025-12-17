# Platform-Native UX Scoring Probe

## Objective
Explore a lightweight, Lighthouse-style CLI that measures how “browser-native” a site’s critical flows feel, using heuristic DOM/network metrics and an optional no-JavaScript replay.

## Background
Modern sites often rely heavily on client-side routing and custom UI controls. This research spike prototypes an automated probe—powered by Playwright—that walks scripted flows, collects DOM and network hints about progressive enhancement, and emits scores summarizing platform-native behaviours.

## Methodology
- **Flow configs (YAML):** Describe a base URL and one or more flows consisting of simple steps (`goto`, `click`, `fill`, `waitForSelector`).
- **Playwright runs:** For each flow, drive Chromium to execute the steps, attaching listeners for navigation and network events.
- **DOM sampling:** After every step, collect semantic/a11y and form-related metrics (anchors, labelled controls, semantic containers, faux click targets, etc.).
- **Network summarisation:** Count XHR/fetch calls, cache headers, and duplicate requests.
- **No-JS replay:** Optionally rerun the flow with JavaScript disabled to gauge progressive enhancement resilience.
- **Scoring:** Convert raw metrics into category scores (routing, forms, data fetching, PE, semantics/a11y) and combine into an overall platform-native score.

## Setup
1. Install Node 20+ and npm.
2. From `code/`, install dependencies:
   ```bash
   npm install
   ```
3. Optional: type-check without emitting output:
   ```bash
   npm run lint
   ```

## Running the probe
1. Edit or reuse `flows.example.yaml` at the repo root. It now covers multiple popular properties (each may override the `baseUrl`):
   - `ajfisher-strategy-article`: `/` → `/tagged/strategy/` → `/2025/11/05/strategy-ai/`
   - `amazon-search-results`: Amazon homepage → wireless mouse search results
   - `wikipedia-browser-topic`: Main page → browser article → accessibility article
   - `mozilla-firefox-download`: Mozilla landing → Firefox download page
2. Execute the CLI from `code/`:
   ```bash
   npm start -- --config ../flows.example.yaml --out ../results/reports/report.json --html ../results/reports/report.html --md ../results/reports/report.md --headless true
   ```
   - Add `--no-js-run` to skip the JavaScript-disabled replay even if the config requests it.
   - Add `--md` to emit a Markdown report in addition to JSON/HTML.
3. Inspect the generated JSON report for per-flow scores and raw metrics, open the HTML report for a weighted score table with a visualised platform-native total, or read the Markdown report for a text-only summary.

## Results
Run the example flows to produce `results/reports/report.json` (JSON), `results/reports/report.html` (visual summary with an overall score bar chart), and `results/reports/report.md` (text-only summary). These capture per-step DOM/network samples alongside flow-level aggregates and scores.

## Score meanings and platform-native total
- **Routing (25%)**: Preference for real document navigations and semantic click targets; penalises heavy client-router hints.
- **Forms (25%)**: Presence of real forms and constrained native controls; penalises faux click targets acting as controls. If no forms are detected in the flow, this category is omitted and the remaining weights are renormalised.
- **Data fetching (20%)**: Rewards cached or server-driven flows; penalises duplicate or uncached XHR/fetch calls.
- **Progressive enhancement (20%)**: Ratio of steps succeeding with JavaScript disabled.
- **Semantics & a11y (10%)**: Semantic landmarks and labelled controls; penalises role misuse and non-semantic clickables.

The **Platform-native total** is a weighted average of the above categories using the percentages listed, recalculated across whichever scores are available for a given flow.

## Conclusions
- A small Playwright harness can surface platform-native heuristics (navigation style, form semantics, caching, and PE) with minimal config.
- Heuristic scoring keeps the probe deterministic yet tunable for future refinement.

## Future Work
- Capture per-step timing and paint metrics for richer routing analysis.
- Expand action vocabulary (e.g., `press`, `selectOption`) and add resilience utilities (timeouts, retries).
- Allow per-flow base URLs or batching across multiple domains without duplicating configs.
- Add richer visualisations (e.g., per-category radar comparisons) to complement the bar chart.

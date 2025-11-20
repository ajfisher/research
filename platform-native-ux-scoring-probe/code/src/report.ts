import fs from 'fs';
import path from 'path';
import { SCORE_WEIGHTS, computeScores } from './scoring';
import { FlowDefinition, FlowMetrics, FlowReport, ProbeReport } from './types';

export function buildFlowReport(baseUrl: string, flow: FlowDefinition, metrics: FlowMetrics): FlowReport {
  const scores = computeScores(metrics);
  return {
    name: flow.name,
    description: flow.description,
    baseUrl,
    jsEnabled: flow.jsEnabled ?? true,
    runNoJs: flow.runNoJs ?? false,
    scores,
    rawMetrics: metrics,
  };
}

export function buildProbeReport(baseUrl: string, flows: FlowReport[]): ProbeReport {
  return {
    baseUrl,
    generatedAt: new Date().toISOString(),
    flows,
  };
}

export function writeReport(outPath: string, report: ProbeReport): void {
  const dir = path.dirname(outPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf-8');
}

function formatScore(value: number | null | undefined): string {
  return value === null || value === undefined ? '—' : String(value);
}

export function renderMarkdownReport(report: ProbeReport): string {
  const lines: string[] = [];
  lines.push('# Platform-Native UX Probe Report');
  lines.push('');
  lines.push(`Generated at: ${report.generatedAt}`);
  lines.push(`Default base URL: ${report.baseUrl}`);
  lines.push('');
  lines.push('## Score meanings & weights');
  lines.push('- **Routing** (' + SCORE_WEIGHTS.routing * 100 + '%): Prefers document navigations and semantic click targets; penalises heavy client-router hints.');
  lines.push('- **Forms** (' + SCORE_WEIGHTS.forms * 100 + '%): Presence of native forms and constrained controls; penalises faux click targets acting as controls. If no forms are found, this score is omitted and the remaining weights are renormalised.');
  lines.push('- **Data fetching** (' + SCORE_WEIGHTS.dataFetch * 100 + '%): Rewards cached or server-driven flows; penalises duplicate or uncached XHR/fetch calls.');
  lines.push('- **Progressive enhancement** (' + SCORE_WEIGHTS.progressiveEnhancement * 100 + '%): Ratio of steps succeeding with JavaScript disabled.');
  lines.push('- **Semantics & a11y** (' + SCORE_WEIGHTS.semanticsA11y * 100 + '%): Semantic landmarks and labelled controls; penalises role misuse and non-semantic clickables.');
  lines.push('');
  lines.push('The **Platform-native total** is a weighted average of available categories; unavailable scores (e.g., no forms detected) are dropped and remaining weights are reapplied.');
  lines.push('');
  lines.push('## Flow summary');
  lines.push('| Flow | Base URL | Routing | Forms | Data fetching | PE (no-JS) | Semantics/a11y | Platform-native total |');
  lines.push('| --- | --- | --- | --- | --- | --- | --- | --- |');
  report.flows.forEach(flow => {
    lines.push(
      `| ${flow.name} | ${flow.baseUrl} | ${formatScore(flow.scores.routing)} | ${formatScore(flow.scores.forms)} | ${formatScore(flow.scores.dataFetch)} | ${formatScore(flow.scores.progressiveEnhancement)} | ${formatScore(flow.scores.semanticsA11y)} | **${formatScore(flow.scores.overall)}** |`
    );
  });
  lines.push('');

  lines.push('## Flow details');
  report.flows.forEach(flow => {
    lines.push(`### ${flow.name}`);
    lines.push(`Base URL: ${flow.baseUrl}${flow.runNoJs ? ' · No-JS replay enabled' : ''}`);
    if (flow.description) {
      lines.push(flow.description);
    }
    lines.push('');
    lines.push('Scores:');
    lines.push(
      `- Routing: ${formatScore(flow.scores.routing)}, Forms: ${formatScore(flow.scores.forms)}, Data fetching: ${formatScore(flow.scores.dataFetch)}, PE: ${formatScore(flow.scores.progressiveEnhancement)}, Semantics & a11y: ${formatScore(flow.scores.semanticsA11y)}, **Platform-native total: ${formatScore(flow.scores.overall)}**`
    );
    lines.push('');
    lines.push('Step metrics:');
    flow.rawMetrics.stepMetrics.forEach(step => {
      const dom = step.domMetrics;
      const networkCount = step.networkEvents.length;
      lines.push(
        `- Step ${step.stepIndex + 1} (${step.step.action}): URL ${dom.url}; anchors ${dom.anchorCount}; forms ${dom.formCount}; controls ${dom.controlCount} (labelled ${dom.labelledControlCount}); non-semantic clickables ${dom.nonSemanticClickableCount}; semantic containers ${dom.semanticContainerCount}; network events ${networkCount}`
      );
    });
    lines.push('');
  });

  return lines.join('\n');
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function renderHtmlReport(report: ProbeReport): string {
  const summaryRows = report.flows
    .map(
      flow => `
        <tr>
          <td>${escapeHtml(flow.name)}</td>
          <td>${escapeHtml(flow.baseUrl)}</td>
          <td>${flow.scores.routing}</td>
          <td>${flow.scores.forms ?? '—'}</td>
          <td>${flow.scores.dataFetch}</td>
          <td>${flow.scores.progressiveEnhancement ?? '—'}</td>
          <td>${flow.scores.semanticsA11y}</td>
          <td><strong>${flow.scores.overall}</strong></td>
        </tr>
      `
    )
    .join('');

  const flowDetails = report.flows
    .map(flow => {
      const steps = flow.rawMetrics.stepMetrics
        .map(step => {
          const dom = step.domMetrics;
          const networkCount = step.networkEvents.length;
          return `
            <li><strong>Step ${step.stepIndex + 1} (${escapeHtml(step.step.action)})</strong>
              <div>URL: ${escapeHtml(dom.url)}</div>
              <div>Anchors: ${dom.anchorCount}, Forms: ${dom.formCount}, Controls: ${dom.controlCount}, Labelled: ${dom.labelledControlCount}</div>
              <div>Non-semantic clickables: ${dom.nonSemanticClickableCount}, Semantic containers: ${dom.semanticContainerCount}</div>
              <div>Network events: ${networkCount}</div>
            </li>
          `;
        })
        .join('');

      return `
        <section class="flow-card">
          <h3>${escapeHtml(flow.name)}</h3>
          <p class="muted">Base URL: ${escapeHtml(flow.baseUrl)}${flow.runNoJs ? ' · No-JS replay enabled' : ''}</p>
          <p>${escapeHtml(flow.description ?? 'No description provided.')}</p>
          <div class="scores">
            <div><span>Routing</span><strong>${flow.scores.routing}</strong></div>
            <div><span>Forms</span><strong>${flow.scores.forms ?? '—'}</strong></div>
            <div><span>Data fetching</span><strong>${flow.scores.dataFetch}</strong></div>
            <div><span>Progressive enhancement</span><strong>${flow.scores.progressiveEnhancement ?? '—'}</strong></div>
            <div><span>Semantics & a11y</span><strong>${flow.scores.semanticsA11y}</strong></div>
            <div class="overall"><span>Platform-native total</span><strong>${flow.scores.overall}</strong></div>
          </div>
          <details>
            <summary>Step metrics</summary>
            <ol>
              ${steps}
            </ol>
          </details>
        </section>
      `;
    })
    .join('');

  return `<!doctype html>
  <html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Platform-Native UX Probe Report</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; padding: 24px; background: #f7f7f9; color: #121212; }
      h1, h2, h3 { margin: 0 0 8px; }
      .muted { color: #555; font-size: 0.9rem; }
      table { width: 100%; border-collapse: collapse; margin: 16px 0; background: #fff; }
      th, td { border: 1px solid #e0e0e0; padding: 8px 10px; text-align: left; }
      th { background: #f0f0f2; }
      .chart-container { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 12px; margin: 12px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow-x: auto; }
      .scores { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; margin: 12px 0; }
      .scores div { background: #f9f9fb; border: 1px solid #e5e5e8; padding: 8px 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: baseline; }
      .scores .overall { background: #0b5ed7; color: #fff; border-color: #0b5ed7; }
      .flow-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
      details { margin-top: 10px; }
      summary { cursor: pointer; color: #0b5ed7; }
      ol { padding-left: 20px; }
    </style>
  </head>
  <body>
    <header>
      <h1>Platform-Native UX Probe</h1>
      <p class="muted">Generated at ${escapeHtml(report.generatedAt)}</p>
      <p class="muted">Default base URL: ${escapeHtml(report.baseUrl)}</p>
    </header>

    <section>
      <h2>Score meanings & weights</h2>
      <ul>
        <li><strong>Routing</strong> (${SCORE_WEIGHTS.routing * 100}%): Preference for document navigations and semantic click targets; penalises heavy client-router hints.</li>
        <li><strong>Forms</strong> (${SCORE_WEIGHTS.forms * 100}%): Presence of real forms and constrained native controls; penalises faux click targets acting as controls. If no forms are found, this score is omitted and the remaining weights are renormalised.</li>
        <li><strong>Data fetching</strong> (${SCORE_WEIGHTS.dataFetch * 100}%): Rewards cached or server-driven flows; penalises duplicate or uncached XHR/fetch calls.</li>
        <li><strong>Progressive enhancement</strong> (${SCORE_WEIGHTS.progressiveEnhancement * 100}%): Ratio of steps succeeding with JavaScript disabled.</li>
        <li><strong>Semantics & a11y</strong> (${SCORE_WEIGHTS.semanticsA11y * 100}%): Semantic landmarks and labelled controls; penalises role misuse and non-semantic clickables.</li>
      </ul>
      <p>The <strong>Platform-native total</strong> is a weighted average of the above scores (weights shown in parentheses). Categories with unavailable scores (e.g., no forms detected) are dropped and the remaining weights are re-applied proportionally.</p>
    </section>

    <section>
      <h2>Platform-native totals (chart)</h2>
      <p class="muted">Per-flow weighted scores visualised for quick comparison.</p>
      <div class="chart-container">
        <canvas id="overallChart" height="320"></canvas>
      </div>
    </section>

    <section>
      <h2>Flow summary</h2>
      <table>
        <thead>
          <tr>
            <th>Flow</th>
            <th>Base URL</th>
            <th>Routing</th>
            <th>Forms</th>
            <th>Data fetching</th>
            <th>PE (no-JS)</th>
            <th>Semantics/a11y</th>
            <th>Platform-native total</th>
          </tr>
        </thead>
        <tbody>
          ${summaryRows}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Flow details</h2>
      ${flowDetails}
    </section>

    <script type="application/json" id="report-data">${escapeHtml(JSON.stringify(report))}</script>
    <script>
      const chartDataEl = document.getElementById('report-data');
      const chartData = chartDataEl ? JSON.parse(chartDataEl.textContent || '{}') : null;
      const canvas = document.getElementById('overallChart');
      if (chartData && canvas) {
        const flows = chartData.flows || [];
        const ctx = canvas.getContext('2d');
        const barWidth = 48;
        const gap = 28;
        const padding = 60;
        const width = Math.max(320, flows.length * (barWidth + gap) + padding * 2);
        canvas.width = width;
        const height = canvas.height;
        if (ctx) {
          ctx.clearRect(0, 0, width, height);
          ctx.strokeStyle = '#888';
          ctx.beginPath();
          ctx.moveTo(padding, 20);
          ctx.lineTo(padding, height - padding);
          ctx.lineTo(width - padding, height - padding);
          ctx.stroke();

          ctx.font = '12px system-ui, sans-serif';
          ctx.fillStyle = '#555';
          ctx.fillText('Score', 10, 24);
          ctx.fillText('Flows', width - padding - 30, height - padding + 24);

          const yMax = height - padding - 10;
          for (let mark = 0; mark <= 100; mark += 20) {
            const y = yMax - (mark / 100) * (height - padding * 2 - 10);
            ctx.fillText(String(mark), padding - 36, y + 4);
            ctx.strokeStyle = '#e5e5e5';
            ctx.beginPath();
            ctx.moveTo(padding - 6, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
          }

          flows.forEach((flow, idx) => {
            const x = padding + idx * (barWidth + gap);
            const barHeight = (flow.scores.overall / 100) * (height - padding * 2 - 10);
            const y = height - padding - barHeight;
            ctx.fillStyle = '#0b5ed7';
            ctx.fillRect(x, y, barWidth, barHeight);

            ctx.fillStyle = '#111';
            ctx.textAlign = 'center';
            ctx.fillText(String(flow.scores.overall), x + barWidth / 2, y - 6);

            const label = flow.name.length > 14 ? flow.name.slice(0, 12) + '…' : flow.name;
            ctx.save();
            ctx.translate(x + barWidth / 2, height - padding + 14);
            ctx.rotate(-Math.PI / 6);
            ctx.fillText(label, 0, 0);
            ctx.restore();
          });
        }
      }
    </script>
  </body>
  </html>`;
}

export function writeHtmlReport(outPath: string, report: ProbeReport): void {
  const html = renderHtmlReport(report);
  const dir = path.dirname(outPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(outPath, html, 'utf-8');
}

export function writeMarkdownReport(outPath: string, report: ProbeReport): void {
  const markdown = renderMarkdownReport(report);
  const dir = path.dirname(outPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(outPath, markdown, 'utf-8');
}

import fs from 'fs';
import YAML from 'yaml';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import { runFlow } from './runner';
import { buildFlowReport, buildProbeReport, writeHtmlReport, writeMarkdownReport, writeReport } from './report';
import { FlowConfig, FlowDefinition } from './types';

function loadConfig(path: string): FlowConfig {
  if (!fs.existsSync(path)) {
    throw new Error(`Config file not found: ${path}`);
  }
  const content = fs.readFileSync(path, 'utf-8');
  const parsed = YAML.parse(content) as FlowConfig;
  if (!parsed.baseUrl || !parsed.flows || !Array.isArray(parsed.flows)) {
    throw new Error('Invalid config: missing baseUrl or flows array');
  }
  return parsed;
}

async function run(): Promise<void> {
  const argv = await yargs(hideBin(process.argv))
    .option('config', { type: 'string', demandOption: true, describe: 'Path to YAML flow config' })
    .option('out', { type: 'string', demandOption: true, describe: 'Path to write JSON report' })
    .option('html', { type: 'string', describe: 'Optional path to write an HTML report' })
    .option('md', { type: 'string', describe: 'Optional path to write a Markdown report' })
    .option('headless', { type: 'boolean', default: true, describe: 'Run browser in headless mode' })
    .option('no-js-run', { type: 'boolean', default: false, describe: 'Skip no-JS runs even if config requests them' })
    .help()
    .parse();

  const config = loadConfig(argv.config);
  const flows: FlowDefinition[] = config.flows.map(flow =>
    argv['no-js-run'] ? { ...flow, runNoJs: false } : flow
  );

  const flowReports = [];
  for (const flow of flows) {
    // eslint-disable-next-line no-console
    console.log(`Running flow: ${flow.name}`);
    const flowBase = flow.baseUrl ?? config.baseUrl;
    const metrics = await runFlow(flowBase, flow, argv.headless);
    const report = buildFlowReport(flowBase, flow, metrics);
    flowReports.push(report);
  }

  const probeReport = buildProbeReport(config.baseUrl, flowReports);
  writeReport(argv.out, probeReport);
  if (argv.html) {
    writeHtmlReport(argv.html, probeReport);
  }
  if (argv.md) {
    writeMarkdownReport(argv.md, probeReport);
  }
  // eslint-disable-next-line no-console
  console.log(`Report written to ${argv.out}`);
  if (argv.html) {
    // eslint-disable-next-line no-console
    console.log(`HTML report written to ${argv.html}`);
  }
  if (argv.md) {
    // eslint-disable-next-line no-console
    console.log(`Markdown report written to ${argv.md}`);
  }
}

run().catch(err => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});

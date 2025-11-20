import { chromium, Page } from 'playwright';
import { collectDomMetrics } from './metrics';
import {
  DomAggregate,
  DomMetrics,
  FlowDefinition,
  FlowMetrics,
  FlowStep,
  NetworkEvent,
  NetworkSummary,
  NoJsStepResult,
  StepMetrics,
} from './types';

function resolveUrl(baseUrl: string, path?: string): string {
  if (!path) return baseUrl;
  try {
    return new URL(path, baseUrl).toString();
  } catch (err) {
    return path;
  }
}

function aggregateDomMetrics(metricsList: DomMetrics[]): DomAggregate {
  const initial: DomAggregate = {
    anchorCount: 0,
    nonSemanticClickableCount: 0,
    url: '',
    formCount: 0,
    controlCount: 0,
    constrainedControlCount: 0,
    fauxControlCount: 0,
    semanticContainerCount: 0,
    labelledControlCount: 0,
    roleButtonOrLinkNonNativeCount: 0,
    hasClientRouterSignatures: false,
    pagesSeen: 0,
  };

  return metricsList.reduce<DomAggregate>((agg, curr) => {
    return {
      anchorCount: agg.anchorCount + curr.anchorCount,
      nonSemanticClickableCount: agg.nonSemanticClickableCount + curr.nonSemanticClickableCount,
      url: curr.url,
      formCount: agg.formCount + curr.formCount,
      controlCount: agg.controlCount + curr.controlCount,
      constrainedControlCount: agg.constrainedControlCount + curr.constrainedControlCount,
      fauxControlCount: agg.fauxControlCount + curr.fauxControlCount,
      semanticContainerCount: agg.semanticContainerCount + curr.semanticContainerCount,
      labelledControlCount: agg.labelledControlCount + curr.labelledControlCount,
      roleButtonOrLinkNonNativeCount: agg.roleButtonOrLinkNonNativeCount + curr.roleButtonOrLinkNonNativeCount,
      hasClientRouterSignatures: agg.hasClientRouterSignatures || curr.hasClientRouterSignatures,
      pagesSeen: agg.pagesSeen + 1,
    };
  }, initial);
}

function summarizeNetwork(events: NetworkEvent[]): NetworkSummary {
  const xhrEvents = events.filter(ev => ['fetch', 'xhr'].includes(ev.resourceType));
  const duplicateMap = new Map<string, number>();

  xhrEvents.forEach(ev => {
    const key = `${ev.method}:${ev.url}`;
    duplicateMap.set(key, (duplicateMap.get(key) || 0) + 1);
  });

  const duplicateRequestCount = Array.from(duplicateMap.values()).filter(count => count > 1).reduce((a, b) => a + (b - 1), 0);
  const uncachedXhrCount = xhrEvents.filter(ev => !ev.cacheControl && !ev.etag).length;

  return {
    xhrCount: xhrEvents.length,
    uncachedXhrCount,
    duplicateRequestCount,
  };
}

async function runStep(page: Page, baseUrl: string, step: FlowStep): Promise<void> {
  switch (step.action) {
    case 'goto': {
      const target = resolveUrl(baseUrl, step.url);
      await page.goto(target, { waitUntil: 'load' });
      break;
    }
    case 'click': {
      if (!step.locator) throw new Error('Missing locator for click step');
      await page.click(step.locator);
      break;
    }
    case 'fill': {
      if (!step.locator) throw new Error('Missing locator for fill step');
      await page.fill(step.locator, step.value ?? '');
      break;
    }
    case 'waitForSelector': {
      if (!step.locator) throw new Error('Missing locator for waitForSelector step');
      await page.waitForSelector(step.locator);
      break;
    }
    default:
      throw new Error(`Unsupported action: ${step.action}`);
  }
}

async function runNoJsFlow(baseUrl: string, flow: FlowDefinition): Promise<NoJsStepResult[]> {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ javaScriptEnabled: false, ignoreHTTPSErrors: true });
  const page = await context.newPage();
  const outcomes: NoJsStepResult[] = [];

  for (const [index, step] of flow.steps.entries()) {
    try {
      if (step.action === 'goto') {
        const target = resolveUrl(baseUrl, step.url);
        const response = await page.goto(target, { waitUntil: 'load' });
        const ok = response ? response.status() < 400 : true;
        outcomes.push({ stepIndex: index, outcome: ok ? 'success' : 'failed-navigation' });
      } else {
        await runStep(page, baseUrl, step);
        outcomes.push({ stepIndex: index, outcome: 'success' });
      }
    } catch (err) {
      const outcome: NoJsStepResult = {
        stepIndex: index,
        outcome: step.action === 'goto' ? 'failed-navigation' : 'failed-interaction',
      };
      outcomes.push(outcome);
    }
  }

  await browser.close();
  return outcomes;
}

export async function runFlow(baseUrl: string, flow: FlowDefinition, headless: boolean): Promise<FlowMetrics> {
  const browser = await chromium.launch({ headless });
  const context = await browser.newContext({
    javaScriptEnabled: flow.jsEnabled ?? true,
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  const networkEvents: NetworkEvent[] = [];
  page.on('requestfinished', async req => {
    const res = await req.response();
    const headers = res ? await res.allHeaders() : {};
    networkEvents.push({
      url: req.url(),
      method: req.method(),
      resourceType: req.resourceType(),
      status: res?.status() ?? null,
      cacheControl: headers['cache-control'],
      etag: headers['etag'],
    });
  });

  let documentNavigationCount = 0;
  page.on('framenavigated', frame => {
    if (frame === page.mainFrame()) {
      documentNavigationCount += 1;
    }
  });

  const domMetricsList: DomMetrics[] = [];
  const stepMetrics: StepMetrics[] = [];

  for (const [stepIndex, step] of flow.steps.entries()) {
    const startingEventIndex = networkEvents.length;
    await runStep(page, baseUrl, step);
    const domMetrics = await collectDomMetrics(page);
    domMetricsList.push(domMetrics);

    const eventsForStep = networkEvents.slice(startingEventIndex);
    stepMetrics.push({
      stepIndex,
      step,
      domMetrics,
      networkEvents: eventsForStep,
    });
  }

  const domAggregates = aggregateDomMetrics(domMetricsList);
  const networkSummary = summarizeNetwork(networkEvents);
  const clickStepCount = flow.steps.filter(step => step.action === 'click').length;

  await browser.close();

  const metrics: FlowMetrics = {
    stepMetrics,
    domAggregates,
    networkSummary,
    clickStepCount,
    documentNavigationCount,
  };

  if (flow.runNoJs) {
    metrics.noJsStepResults = await runNoJsFlow(baseUrl, flow);
  }

  return metrics;
}

import { DomAggregate, FlowMetrics, FlowScores } from './types';

const clamp = (value: number, min = 0, max = 100) => Math.min(max, Math.max(min, value));

function routingScore(metrics: FlowMetrics): number {
  const navRatio = Math.min(1, metrics.documentNavigationCount / Math.max(1, metrics.clickStepCount));
  const nonSemanticPenalty = Math.min(1, metrics.domAggregates.nonSemanticClickableCount / 20);
  const routerPenalty = metrics.domAggregates.hasClientRouterSignatures ? 0.2 : 0;
  const base = navRatio;
  const penalty = 0.5 * nonSemanticPenalty + routerPenalty;
  const raw = base * (1 - penalty);
  return clamp(Math.round(100 * raw));
}

function formsScore(dom: DomAggregate): number | null {
  if (dom.formCount === 0) {
    return null;
  }

  const hasForms = dom.formCount > 0 ? 1 : 0;
  const constraintRatio = dom.controlCount > 0 ? dom.constrainedControlCount / dom.controlCount : 0;
  const fauxPenalty = Math.min(1, dom.fauxControlCount / 20);
  const base = 0.4 * hasForms + 0.6 * constraintRatio;
  const raw = base * (1 - 0.5 * fauxPenalty);
  return clamp(Math.round(100 * raw));
}

function dataFetchScore(summary: FlowMetrics['networkSummary']): number {
  const { xhrCount, uncachedXhrCount, duplicateRequestCount } = summary;
  const base = xhrCount === 0 ? 0.8 : (xhrCount - uncachedXhrCount) / Math.max(1, xhrCount);
  const dupPenalty = xhrCount > 0 ? Math.min(1, duplicateRequestCount / xhrCount) : 0;
  const raw = base * (1 - 0.5 * dupPenalty);
  return clamp(Math.round(100 * raw));
}

function progressiveEnhancementScore(results?: FlowMetrics['noJsStepResults']): number | null {
  if (!results) return null;
  const successCount = results.filter(r => r.outcome === 'success').length;
  const ratio = results.length > 0 ? successCount / results.length : 0;
  return clamp(Math.round(100 * ratio));
}

function semanticsScore(dom: DomAggregate): number {
  const hasSemanticContainers = dom.semanticContainerCount > 0 ? 1 : 0;
  const labellingRatio = dom.controlCount > 0 ? dom.labelledControlCount / dom.controlCount : 0;
  const roleAbusePenalty = Math.min(1, dom.roleButtonOrLinkNonNativeCount / 20);
  const clickDivPenalty = Math.min(1, dom.nonSemanticClickableCount / 20);
  const base = 0.3 * hasSemanticContainers + 0.7 * labellingRatio;
  const penalty = 0.4 * roleAbusePenalty + 0.3 * clickDivPenalty;
  const raw = base * (1 - penalty);
  return clamp(Math.round(100 * raw));
}

export const SCORE_WEIGHTS: Record<keyof Omit<FlowScores, 'overall'>, number> = {
  routing: 0.25,
  forms: 0.25,
  dataFetch: 0.2,
  progressiveEnhancement: 0.2,
  semanticsA11y: 0.1,
};

export function computeScores(metrics: FlowMetrics): FlowScores {
  const routing = routingScore(metrics);
  const forms = formsScore(metrics.domAggregates);
  const dataFetch = dataFetchScore(metrics.networkSummary);
  const progressiveEnhancement = progressiveEnhancementScore(metrics.noJsStepResults);
  const semanticsA11y = semanticsScore(metrics.domAggregates);

  const partialScores = { routing, forms, dataFetch, progressiveEnhancement, semanticsA11y };

  let sum = 0;
  let totalWeight = 0;
  (Object.keys(SCORE_WEIGHTS) as (keyof typeof SCORE_WEIGHTS)[]).forEach(key => {
    const val = partialScores[key];
    if (val === null || val === undefined || val < 0) return;
    sum += val * SCORE_WEIGHTS[key];
    totalWeight += SCORE_WEIGHTS[key];
  });

  const overall = totalWeight > 0 ? Math.round(sum / totalWeight) : 0;

  return { routing, forms, dataFetch, progressiveEnhancement, semanticsA11y, overall };
}

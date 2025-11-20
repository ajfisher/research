import { Page } from 'playwright';

export type StepAction = 'goto' | 'click' | 'fill' | 'waitForSelector';

export interface FlowStep {
  action: StepAction;
  url?: string;
  locator?: string;
  value?: string;
  description?: string;
}

export interface FlowConfig {
  baseUrl: string;
  flows: FlowDefinition[];
}

export interface FlowDefinition {
  name: string;
  description?: string;
  baseUrl?: string;
  jsEnabled?: boolean;
  runNoJs?: boolean;
  steps: FlowStep[];
}

export type StepOutcome = 'success' | 'failed-navigation' | 'failed-interaction';

export interface NoJsStepResult {
  stepIndex: number;
  outcome: StepOutcome;
}

export interface DomMetrics {
  anchorCount: number;
  nonSemanticClickableCount: number;
  url: string;
  formCount: number;
  controlCount: number;
  constrainedControlCount: number;
  fauxControlCount: number;
  semanticContainerCount: number;
  labelledControlCount: number;
  roleButtonOrLinkNonNativeCount: number;
  hasClientRouterSignatures: boolean;
}

export interface DomAggregate extends DomMetrics {
  pagesSeen: number;
}

export interface NetworkEvent {
  url: string;
  method: string;
  resourceType: string;
  status: number | null;
  cacheControl?: string;
  etag?: string;
}

export interface NetworkSummary {
  xhrCount: number;
  uncachedXhrCount: number;
  duplicateRequestCount: number;
}

export interface StepMetrics {
  stepIndex: number;
  step: FlowStep;
  domMetrics: DomMetrics;
  networkEvents: NetworkEvent[];
}

export interface FlowMetrics {
  stepMetrics: StepMetrics[];
  domAggregates: DomAggregate;
  networkSummary: NetworkSummary;
  clickStepCount: number;
  documentNavigationCount: number;
  noJsStepResults?: NoJsStepResult[];
}

export interface FlowScores {
  routing: number;
  forms: number | null;
  dataFetch: number;
  progressiveEnhancement: number | null;
  semanticsA11y: number;
  overall: number;
}

export interface FlowReport {
  name: string;
  description?: string;
  baseUrl: string;
  jsEnabled: boolean;
  runNoJs: boolean;
  scores: FlowScores;
  rawMetrics: FlowMetrics;
}

export interface ProbeReport {
  baseUrl: string;
  generatedAt: string;
  flows: FlowReport[];
}

export interface DomMetricsCollector {
  (page: Page): Promise<DomMetrics>;
}

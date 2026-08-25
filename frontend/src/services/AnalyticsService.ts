import { APIClient } from './apiClient';

export interface RevenueData {
  mrr: number;
  arr: number;
  revenue: number;
  api_cost: number;
  gpu_cost: number;
  infra_cost: number;
  profit: number;
  margin: number;
  ltv: number;
  cac: number;
}

export interface QualityCategory {
  category: string;
  score: number;
  tests_passed: number;
  build_success: number;
  deploy_success: number;
  performance: number;
  seo: number;
  accessibility: number;
  security: number;
}

export interface QualityData {
  average_score: number;
  build_success_rate: number;
  deploy_success_rate: number;
  categories: QualityCategory[];
  audit_logs: Array<{
    timestamp: string;
    project: string;
    template: string;
    checks: Record<string, string>;
    final_score: number;
  }>;
}

export interface FunnelStepData {
  step: string;
  label: string;
  users_count: number;
  absolute_conversion_pct: number;
  relative_conversion_pct: number;
  drop_off_pct: number;
  avg_time_ms: number;
  error_rate_pct: number;
  retry_count: number;
}

export interface ProductInsight {
  title: string;
  impact: string;
  description: string;
}

export interface OnboardingProblem {
  rank: number;
  issue: string;
  metric: string;
  impact: string;
  fix: string;
}

export interface IncidentLog {
  id: string;
  step: string;
  timestamp: string;
  error_message: string;
  browser: string;
  device: string;
  workspace_id: string;
  logs_trace: string;
}

export interface BetaProgressMilestone {
  current: number;
  target: number;
  delta?: string;
}

export interface BetaProgressData {
  demo?: boolean;
  registrations: BetaProgressMilestone;
  activated_users: BetaProgressMilestone;
  projects_created: BetaProgressMilestone;
  successful_deploys: BetaProgressMilestone;
  retention: BetaProgressMilestone;
  paying_customers: BetaProgressMilestone;
  revenue: BetaProgressMilestone;
  days_without_bug: BetaProgressMilestone;
  progress_percentage: number;
  next_milestone: string;
  activation_funnel?: {
    registered: number;
    workspace: number;
    gen: number;
    compiled: number;
    deployed: number;
  };
}

export interface ProductIntelligenceData {
  funnel: FunnelStepData[];
  insights: ProductInsight[];
  onboarding_problems: OnboardingProblem[];
  incidents: (IncidentLog & {
    failure_reasoning?: {
      category: string;
      reasoning: string;
      recommendation: string;
    };
  })[];
  live_events_tracked: number;
  segment_counts: {
    all: number;
    new: number;
    power: number;
    paying: number;
  };
  generation_quality: {
    utility_score: number;
    sentiment_distribution: {
      excellent: number;
      good: number;
      friction: number;
      abandoned: number;
    };
    average_edit_count: number;
  };
  customer_success_questions: {
    question: string;
    status: string;
    metric: string;
    reasoning: string;
    recommendation: string;
  }[];
  beta_progress?: BetaProgressData;
}

export class AnalyticsService {
  public static async getRevenueDashboard(): Promise<RevenueData> {
    return APIClient.get<RevenueData>('/api/analytics/revenue/');
  }

  public static async getQualityDashboard(): Promise<QualityData> {
    return APIClient.get<QualityData>('/api/analytics/quality/');
  }

  public static async getProductIntelligence(segment: string = 'all', demo: boolean = true): Promise<ProductIntelligenceData> {
    return APIClient.get<ProductIntelligenceData>(`/api/analytics/product-intelligence/?segment=${segment}&demo=${demo}`);
  }

  public static async getTelemetryDrilldown(metric: string, demo: boolean = true): Promise<any[]> {
    return APIClient.get<any[]>(`/api/analytics/product-intelligence/drilldown/?metric=${metric}&demo=${demo}`);
  }

  public static async postTelemetry(params: {
    step: string;
    status?: 'success' | 'failed' | 'dropped';
    error_message?: string;
    retry_count?: number;
    duration_ms?: number;
    workspace_id?: string;
    logs?: string;
  }): Promise<any> {
    let browser = 'Unknown';
    let device = 'Desktop';
    if (typeof window !== 'undefined') {
      const ua = window.navigator.userAgent;
      if (ua.indexOf("Firefox") > -1) browser = "Firefox";
      else if (ua.indexOf("Chrome") > -1) browser = "Chrome";
      else if (ua.indexOf("Safari") > -1) browser = "Safari";
      else if (ua.indexOf("Edge") > -1) browser = "Edge";

      if (/Mobi|Android|iPhone/i.test(ua)) device = "Mobile";
      else if (/iPad|Tablet/i.test(ua)) device = "Tablet";
    }

    return APIClient.post('/api/analytics/telemetry/', {
      ...params,
      browser,
      device,
      version: 'v1.0.0-rc'
    });
  }
}

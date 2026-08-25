export interface BenchmarkStats {
  averageLatencyMs: number;
  buildSuccessRate: number; // 0 to 1
  averageCostUsd: number;
  totalExecutions: number;
}

export interface SharedWorkflow {
  id: string;
  name: string;
  rating: number; // 1 to 5
  isCompatible: boolean;
}

export class CivilizationFederator {
  private serverId: string;
  private anonymousStats: BenchmarkStats[] = [];

  constructor(serverId: string) {
    this.serverId = serverId;
  }

  public publishStats(stats: BenchmarkStats): void {
    // Anonymously publishes stats to federation memory
    this.anonymousStats.push(stats);
    console.log(`[Civilization Federation] Published stats from server: ${this.serverId}. Executions: ${stats.totalExecutions}`);
  }

  public getGlobalAverages(): BenchmarkStats {
    if (this.anonymousStats.length === 0) {
      return {
        averageLatencyMs: 0,
        buildSuccessRate: 1.0,
        averageCostUsd: 0,
        totalExecutions: 0
      };
    }

    let totalLatency = 0;
    let totalSuccessRate = 0;
    let totalCost = 0;
    let totalExecs = 0;

    for (const s of this.anonymousStats) {
      totalLatency += s.averageLatencyMs;
      totalSuccessRate += s.buildSuccessRate;
      totalCost += s.averageCostUsd;
      totalExecs += s.totalExecutions;
    }

    const count = this.anonymousStats.length;

    return {
      averageLatencyMs: totalLatency / count,
      buildSuccessRate: totalSuccessRate / count,
      averageCostUsd: totalCost / count,
      totalExecutions: totalExecs
    };
  }

  public static generalizeWorkflow(workflow: SharedWorkflow): {
    globalTemplateId: string;
    eligibleForMarketplace: boolean;
  } {
    // Only generalize workflows with excellent rating and platform compatibility
    const eligible = workflow.rating >= 4.5 && workflow.isCompatible;
    const globalTemplateId = `global-tpl-${workflow.id}`;

    return {
      globalTemplateId,
      eligibleForMarketplace: eligible
    };
  }
}

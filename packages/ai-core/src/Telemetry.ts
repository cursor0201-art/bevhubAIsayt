export interface TelemetryRecord {
  taskId: string;
  stepId: string;
  durationMs: number;
  tokensUsed: number;
  cost: number;
  retries: number;
}

export class Telemetry {
  private records: TelemetryRecord[] = [];

  public logMetric(record: TelemetryRecord): void {
    this.records.push(record);
    console.log(
      `[Telemetry] [${record.stepId}] Success in ${record.durationMs}ms | ` +
      `Tokens: ${record.tokensUsed} | Cost: $${record.cost.toFixed(4)}`
    );
  }

  public getSummary(taskId: string): {
    totalDurationMs: number;
    totalTokens: number;
    totalCost: number;
    totalRetries: number;
  } {
    const taskRecords = this.records.filter(r => r.taskId === taskId);
    return taskRecords.reduce(
      (acc, r) => {
        acc.totalDurationMs += r.durationMs;
        acc.totalTokens += r.tokensUsed;
        acc.totalCost += r.cost;
        acc.totalRetries += r.retries;
        return acc;
      },
      { totalDurationMs: 0, totalTokens: 0, totalCost: 0, totalRetries: 0 }
    );
  }
}

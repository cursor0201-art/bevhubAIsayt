import { EventBus } from './EventBus';

export interface ChaosFailure {
  type: 'API_TIMEOUT' | 'REDIS_OFFLINE' | 'LLM_RATE_LIMIT' | 'DATABASE_DISCONNECT';
  severity: 'low' | 'medium' | 'high';
  injectedAt: number;
}

export interface ChaosResult {
  recovered: boolean;
  recoveryDurationMs: number;
  stabilityScore: number;
}

export class ChaosEngine {
  private eventBus: EventBus;
  private activeFailures: ChaosFailure[] = [];

  constructor() {
    this.eventBus = EventBus.getInstance();
  }

  public injectRandomFailure(taskId: string): ChaosFailure {
    const failureTypes: ChaosFailure['type'][] = [
      'API_TIMEOUT',
      'REDIS_OFFLINE',
      'LLM_RATE_LIMIT',
      'DATABASE_DISCONNECT'
    ];

    const chosenType = failureTypes[Math.floor(Math.random() * failureTypes.length)];
    const failure: ChaosFailure = {
      type: chosenType,
      severity: chosenType === 'LLM_RATE_LIMIT' ? 'high' : 'medium',
      injectedAt: Date.now()
    };

    this.activeFailures.push(failure);

    this.eventBus.publish({
      taskId,
      type: 'WARNING',
      sender: 'chaos_engine',
      timestamp: failure.injectedAt,
      data: {
        message: `[Chaos Engine] INJECTED FAILURE: ${failure.type} (Severity: ${failure.severity})`
      }
    });

    return failure;
  }

  public resolveFailures(taskId: string): ChaosResult {
    if (this.activeFailures.length === 0) {
      return { recovered: true, recoveryDurationMs: 0, stabilityScore: 100 };
    }

    const duration = Date.now() - this.activeFailures[0].injectedAt;
    const resolvedCount = this.activeFailures.length;
    this.activeFailures = [];

    // Calculate stability score based on resolving latency
    const stabilityScore = Math.max(50, 100 - resolvedCount * 10 - Math.round(duration / 100));

    this.eventBus.publish({
      taskId,
      type: 'COMPLETED',
      sender: 'chaos_engine',
      timestamp: Date.now(),
      data: {
        message: `[Chaos Engine] RESOLVED all ${resolvedCount} failure(s).`,
        recoveryDurationMs: duration,
        stabilityScore
      }
    });

    return {
      recovered: true,
      recoveryDurationMs: duration,
      stabilityScore
    };
  }
}

export interface DecisionRecord {
  id: string;
  topic: string;
  decision: string;
  rationale: string;
  alternativesConsidered: string[];
  timestamp: number;
}

export interface RepairPattern {
  errorPattern: string;
  resolutionText: string;
  occurrenceCount: number;
}

export class EngineeringMemory {
  private static instance: EngineeringMemory;
  private decisions: DecisionRecord[] = [];
  private repairs: RepairPattern[] = [];

  private constructor() {
    // Populate with historical architectural decisions to demonstrate capability
    this.logDecision({
      id: 'dec-001',
      topic: 'DATABASE_SELECTION',
      decision: 'Selected PostgreSQL over MySQL',
      rationale: 'PostgreSQL provides superior ACID compliance, support for JSONB indices, and relational schemas reliability required for enterprise-grade SaaS billing/multitenancy.',
      alternativesConsidered: ['MySQL', 'MongoDB', 'DynamoDB'],
      timestamp: Date.now() - 8 * 30 * 24 * 60 * 60 * 1000 // 8 months ago
    });

    this.logDecision({
      id: 'dec-002',
      topic: 'CACHE_QUEUES_SELECTION',
      decision: 'Selected Redis over RabbitMQ',
      rationale: 'Redis offers excellent combined capabilities as both a fast memory cache store and Celery task broker backend with lower operational overhead.',
      alternativesConsidered: ['RabbitMQ', 'Amazon SQS'],
      timestamp: Date.now() - 4 * 30 * 24 * 60 * 60 * 1000 // 4 months ago
    });
  }

  public static getInstance(): EngineeringMemory {
    if (!EngineeringMemory.instance) {
      EngineeringMemory.instance = new EngineeringMemory();
    }
    return EngineeringMemory.instance;
  }

  public logDecision(record: DecisionRecord): void {
    this.decisions.push(record);
    console.log(`[Engineering Memory] Logged architectural decision: ${record.decision}`);
  }

  public getDecisionForTopic(topic: string): DecisionRecord | null {
    const match = this.decisions.find(d => d.topic === topic);
    return match || null;
  }

  public logRepair(errorPattern: string, resolution: string): void {
    const existing = this.repairs.find(r => r.errorPattern === errorPattern);
    if (existing) {
      existing.occurrenceCount++;
    } else {
      this.repairs.push({
        errorPattern,
        resolutionText: resolution,
        occurrenceCount: 1
      });
    }
    console.log(`[Engineering Memory] Logged repair pattern for: "${errorPattern}"`);
  }

  public getRepairs(): RepairPattern[] {
    return this.repairs;
  }

  public getDecisions(): DecisionRecord[] {
    return this.decisions;
  }

  public clear(): void {
    this.decisions = [];
    this.repairs = [];
  }
}

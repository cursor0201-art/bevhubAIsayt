export type MutationType = 'IMPROVEMENT' | 'REGRESSION' | 'OPTIMIZATION' | 'REFACTOR';

export interface RepositoryMetric {
  commitsCount: number;
  bugRate: number;
  rollbacksCount: number;
  successfulDeploys: number;
}

export interface MutationRecord {
  type: MutationType;
  description: string;
  impactScore: number; // -10 to +10
}

export class DNAProtocolEngine {
  private baseMetric: RepositoryMetric;
  private mutations: MutationRecord[] = [];

  constructor(initialMetric: RepositoryMetric) {
    this.baseMetric = initialMetric;
  }

  public classifyMutation(change: {
    linesAdded: number;
    hasNewTests: boolean;
    performanceDeltaMs: number;
    introducedVulnerabilitiesCount: number;
  }): MutationRecord {
    if (change.introducedVulnerabilitiesCount > 0) {
      const mutation: MutationRecord = {
        type: 'REGRESSION',
        description: 'Introduced potential security issues or bugs.',
        impactScore: -8
      };
      this.mutations.push(mutation);
      return mutation;
    }

    if (change.performanceDeltaMs < 0 && change.hasNewTests) {
      const mutation: MutationRecord = {
        type: 'OPTIMIZATION',
        description: 'Improved query response latency and expanded test coverage.',
        impactScore: 9
      };
      this.mutations.push(mutation);
      return mutation;
    }

    if (change.hasNewTests) {
      const mutation: MutationRecord = {
        type: 'IMPROVEMENT',
        description: 'New feature added with verification tests.',
        impactScore: 7
      };
      this.mutations.push(mutation);
      return mutation;
    }

    const mutation: MutationRecord = {
      type: 'REFACTOR',
      description: 'Modified code without altering test verification boundary.',
      impactScore: 2
    };
    this.mutations.push(mutation);
    return mutation;
  }

  // Returns overall DNA compliance rating (0 to 100) based on mutations history
  public getDNAComplianceRating(): number {
    if (this.mutations.length === 0) return 100;
    
    let totalScore = 100;
    for (const m of this.mutations) {
      totalScore += m.impactScore;
    }

    // Keep score bounded within 0 - 100 range
    return Math.max(0, Math.min(100, totalScore));
  }
}

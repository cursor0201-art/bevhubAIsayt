export interface DodCriteria {
  minTestCoverage: number;
  maxExecutionTimeSeconds: number;
  maxCostUsd: number;
  requireSuccessfulBuild: boolean;
  requireDeploymentUrl: boolean;
}

export interface ProjectAuditResult {
  projectName: string;
  passesDod: boolean;
  actualTestCoverage: number;
  actualExecutionTimeSeconds: number;
  actualCostUsd: number;
  hasBuildPassed: boolean;
  hasDeploymentUrl: boolean;
  violations: string[];
}

export class DefinitionOfDoneEngine {
  private static readonly STANDARD_CRITERIA: Record<string, DodCriteria> = {
    mvp: {
      minTestCoverage: 30,
      maxExecutionTimeSeconds: 120,
      maxCostUsd: 0.10,
      requireSuccessfulBuild: true,
      requireDeploymentUrl: true
    },
    production: {
      minTestCoverage: 80,
      maxExecutionTimeSeconds: 60,
      maxCostUsd: 0.05,
      requireSuccessfulBuild: true,
      requireDeploymentUrl: true
    }
  };

  public static getCriteria(mode: 'mvp' | 'production'): DodCriteria {
    return this.STANDARD_CRITERIA[mode];
  }

  public static verifyProject(
    projectName: string,
    mode: 'mvp' | 'production',
    metrics: {
      testCoverage: number;
      executionTimeSeconds: number;
      costUsd: number;
      buildPassed: boolean;
      deploymentUrl?: string;
    }
  ): ProjectAuditResult {
    const criteria = this.getCriteria(mode);
    const violations: string[] = [];

    if (metrics.testCoverage < criteria.minTestCoverage) {
      violations.push(`Test coverage (${metrics.testCoverage}%) is below target (${criteria.minTestCoverage}%)`);
    }

    if (metrics.executionTimeSeconds > criteria.maxExecutionTimeSeconds) {
      violations.push(`Execution duration (${metrics.executionTimeSeconds}s) exceeded limit (${criteria.maxExecutionTimeSeconds}s)`);
    }

    if (metrics.costUsd > criteria.maxCostUsd) {
      violations.push(`Generation cost ($${metrics.costUsd.toFixed(4)}) exceeded limit ($${criteria.maxCostUsd.toFixed(4)})`);
    }

    if (criteria.requireSuccessfulBuild && !metrics.buildPassed) {
      violations.push('Project compilation or local build failed.');
    }

    if (criteria.requireDeploymentUrl && !metrics.deploymentUrl) {
      violations.push('No preview deployment URL assigned.');
    }

    return {
      projectName,
      passesDod: violations.length === 0,
      actualTestCoverage: metrics.testCoverage,
      actualExecutionTimeSeconds: metrics.executionTimeSeconds,
      actualCostUsd: metrics.costUsd,
      hasBuildPassed: metrics.buildPassed,
      hasDeploymentUrl: !!metrics.deploymentUrl,
      violations
    };
  }
}

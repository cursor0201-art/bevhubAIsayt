export type ProjectPersonality = 'startup' | 'enterprise' | 'open-source' | 'banking';

export interface GenomeSignature {
  architectureStyle: string;
  namingConvention: 'camelCase' | 'snake_case';
  performanceTargetMs: number;
  minTestCoverage: number;
  securityStrictness: number; // 0 to 100
}

export class EngineeringGenome {
  public personality: ProjectPersonality;
  public signature: GenomeSignature;
  public genomeVersion: number = 1.0;

  constructor(personality: ProjectPersonality) {
    this.personality = personality;
    this.signature = this.calculateInitialSignature(personality);
  }

  private calculateInitialSignature(personality: ProjectPersonality): GenomeSignature {
    switch (personality) {
      case 'startup':
        return {
          architectureStyle: 'layered-monolith',
          namingConvention: 'camelCase',
          performanceTargetMs: 800,
          minTestCoverage: 30,
          securityStrictness: 40
        };
      case 'enterprise':
        return {
          architectureStyle: 'hexagonal-architecture',
          namingConvention: 'camelCase',
          performanceTargetMs: 300,
          minTestCoverage: 90,
          securityStrictness: 95
        };
      case 'banking':
        return {
          architectureStyle: 'microservices',
          namingConvention: 'snake_case',
          performanceTargetMs: 150,
          minTestCoverage: 100,
          securityStrictness: 100
        };
      case 'open-source':
      default:
        return {
          architectureStyle: 'modular-monolith',
          namingConvention: 'camelCase',
          performanceTargetMs: 500,
          minTestCoverage: 70,
          securityStrictness: 70
        };
    }
  }

  // Evolves project genome DNA signature based on code changes metrics
  public evolveGenome(metrics: {
    linesOfCodeAdded: number;
    testFilesCreated: number;
    securityVulnerabilitiesResolved: number;
  }): void {
    this.genomeVersion = Math.round((this.genomeVersion + 0.1) * 10) / 10;

    if (metrics.testFilesCreated > 5) {
      this.signature.minTestCoverage = Math.min(100, this.signature.minTestCoverage + 10);
    }
    if (metrics.securityVulnerabilitiesResolved > 3) {
      this.signature.securityStrictness = Math.min(100, this.signature.securityStrictness + 5);
    }

    console.log(
      `[Genome evolved] Version up to v${this.genomeVersion}. ` +
      `Test Coverage Target: ${this.signature.minTestCoverage}%, Strictness: ${this.signature.securityStrictness}%`
    );
  }

  // Generates prompt instructions customized for this project's personality genome
  public getGenomePromptDirectives(): string {
    return (
      `=== GENOME SYSTEM DIRECTIVES ===\n` +
      `Personality Mode    : ${this.personality.toUpperCase()}\n` +
      `Architecture style  : ${this.signature.architectureStyle}\n` +
      `Naming Convention   : ${this.signature.namingConvention}\n` +
      `Test coverage min   : ${this.signature.minTestCoverage}%\n` +
      `Security strictness : ${this.signature.securityStrictness}/100\n` +
      `Performance latency : < ${this.signature.performanceTargetMs}ms\n` +
      `================================\n`
    );
  }
}

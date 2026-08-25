export interface CandidateOption {
  title: string;
  architecture: number; // 0 to 10
  security: number;     // 0 to 10
  maintainability: number; // 0 to 10
  deploymentSuccess: number; // 0 to 1
  userSatisfaction: number;  // 0 to 10
  cost: number;         // Positive USD cost
  latency: number;      // Seconds
}

export interface OptimizationStepResult {
  iteration: number;
  bestOption: CandidateOption;
  utilityScore: number;
}

export class UtilityOptimizer {
  public static calculateUtility(option: CandidateOption): number {
    const numerator =
      option.architecture *
      option.security *
      option.maintainability *
      option.deploymentSuccess *
      option.userSatisfaction;
    
    // Ensure denominators are positive and non-zero
    const adjustedCost = Math.max(0.01, option.cost);
    const adjustedLatency = Math.max(0.1, option.latency);

    return numerator / (adjustedCost * adjustedLatency);
  }

  public static findOptimalCandidate(candidates: CandidateOption[]): {
    best: CandidateOption;
    score: number;
  } {
    if (candidates.length === 0) {
      throw new Error('No candidate options provided to optimizer.');
    }

    let bestCandidate = candidates[0];
    let maxScore = this.calculateUtility(bestCandidate);

    for (let i = 1; i < candidates.length; i++) {
      const currentScore = this.calculateUtility(candidates[i]);
      if (currentScore > maxScore) {
        maxScore = currentScore;
        bestCandidate = candidates[i];
      }
    }

    return {
      best: bestCandidate,
      score: maxScore
    };
  }

  // Simulates optimization loop iterations adjusting parameters for max utility
  public static runOptimizationLoop(
    baseOption: CandidateOption,
    iterations: number = 3
  ): OptimizationStepResult[] {
    const results: OptimizationStepResult[] = [];
    let currentOption = { ...baseOption };

    for (let i = 1; i <= iterations; i++) {
      // Predict & Optimize adjustments (e.g. increase security, lower latency/cost by optimizing code templates)
      currentOption.security = Math.min(10, currentOption.security + 0.5);
      currentOption.latency = Math.max(0.2, currentOption.latency - 0.3);
      currentOption.cost = Math.max(0.02, currentOption.cost - 0.01);

      const utilityScore = this.calculateUtility(currentOption);
      results.push({
        iteration: i,
        bestOption: { ...currentOption },
        utilityScore
      });
    }

    return results;
  }
}

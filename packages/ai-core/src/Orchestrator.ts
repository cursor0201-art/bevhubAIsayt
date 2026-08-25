import { EventBus } from './EventBus';
import { ContextEngine, ContextSource, ContextPackage } from './ContextEngine';
import { Planner, ExecutionPlan } from './Planner';
import { Compiler } from './Compiler';
import { Runtime, StepExecutionResult } from './Runtime';
import { Telemetry } from './Telemetry';
import { Memory } from './Memory';

export interface OrchestrationResult {
  taskId: string;
  success: boolean;
  requestClass: string;
  plan: ExecutionPlan;
  stepsCount: number;
  results: StepExecutionResult[];
  summary: {
    totalDurationMs: number;
    totalTokens: number;
    totalCost: number;
    totalRetries: number;
  };
}

export class Orchestrator {
  private eventBus: EventBus;
  private telemetry: Telemetry;
  private memory: Memory;

  constructor() {
    this.eventBus = EventBus.getInstance();
    this.telemetry = new Telemetry();
    this.memory = Memory.getInstance();
  }

  public async runOrchestration(
    taskId: string,
    prompt: string,
    sources: ContextSource[]
  ): Promise<OrchestrationResult> {
    console.log(`[Orchestrator] Starting orchestration sequence for task: ${taskId}`);

    // Publish global request init event
    this.eventBus.publish({
      taskId,
      type: 'REQUEST',
      sender: 'orchestrator',
      timestamp: Date.now(),
      data: { prompt }
    });

    // 1. Context Selection
    const contextPackage = ContextEngine.scoreAndSelectContext(prompt, sources);
    this.memory.set(`${taskId}:context`, contextPackage);

    // 2. Planning (build DAG)
    const plan = Planner.createExecutionPlan(taskId, prompt, contextPackage);
    this.memory.set(`${taskId}:plan`, plan);

    // 3. Compilation (topological step resolution)
    const steps = Compiler.compilePlan(plan);
    this.memory.set(`${taskId}:steps`, steps);

    // 4. Runtime Step Loop Execution
    const runtime = new Runtime(this.telemetry);
    const results: StepExecutionResult[] = [];
    let success = true;

    for (const step of steps) {
      // Publish step PROGRESS
      this.eventBus.publish({
        taskId,
        type: 'PROGRESS',
        sender: 'orchestrator',
        timestamp: Date.now(),
        data: { currentStep: step.name, percent: Math.round((results.length / steps.length) * 100) }
      });

      const stepResult = await runtime.executeStep(taskId, step);
      results.push(stepResult);

      if (!stepResult.success) {
        success = false;
        break;
      }
    }

    const summary = this.telemetry.getSummary(taskId);

    // Final result compilation
    const finalResult: OrchestrationResult = {
      taskId,
      success,
      requestClass: contextPackage.requestClass,
      plan,
      stepsCount: steps.length,
      results,
      summary
    };

    // Store final state in memory
    this.memory.set(`${taskId}:result`, finalResult);

    console.log(`[Orchestrator] Finished task orchestration: ${success ? 'SUCCESS' : 'FAILED'}`);
    return finalResult;
  }
}

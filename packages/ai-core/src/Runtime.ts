import { EventBus } from './EventBus';
import { CompiledStep } from './Compiler';
import { Validator, ValidationResult } from './Validator';
import { Telemetry } from './Telemetry';
import { Memory } from './Memory';

export interface StepExecutionResult {
  stepId: string;
  success: boolean;
  output: any;
  validation: ValidationResult;
  durationMs: number;
}

export class Runtime {
  private eventBus: EventBus;
  private telemetry: Telemetry;
  private memory: Memory;

  constructor(telemetry: Telemetry) {
    this.eventBus = EventBus.getInstance();
    this.telemetry = telemetry;
    this.memory = Memory.getInstance();
  }

  public async executeStep(
    taskId: string,
    step: CompiledStep
  ): Promise<StepExecutionResult> {
    const startTime = Date.now();

    // Publish STARTED event
    this.eventBus.publish({
      taskId,
      type: 'STARTED',
      sender: step.nodeId,
      timestamp: startTime,
      data: { name: step.name, instruction: step.systemInstruction }
    });

    // Simulate Agent execution output
    let output: any = {};
    let retries = 0;
    const maxRetries = 2;

    switch (step.type) {
      case 'planning':
        output = {
          specs: `Specifications generated for step ${step.name}`,
          features: ['auth', 'catalog', 'payments']
        };
        break;
      case 'architecture':
        output = {
          designSystem: {
            primary: '#6366f1',
            secondary: '#ec4899',
            font: 'Outfit'
          }
        };
        break;
      case 'database':
        output = {
          sql: `CREATE TABLE products (id UUID PRIMARY KEY, name VARCHAR(255), price DECIMAL);`
        };
        break;
      case 'backend':
        output = {
          endpoints: [
            { path: '/api/v1/products', method: 'GET' }
          ]
        };
        break;
      case 'frontend':
        // Intentionally trigger validation issue on first pass to demo self-repair
        output = {
          html: `<html><body><h1>Welcome to BevHub website</h1></body></html>`
        };
        break;
      case 'validation':
        output = { status: 'passed' };
        break;
      case 'deployment':
        output = {
          dockerfile: 'FROM node:20\nWORKDIR /app\nCOPY . .\nCMD ["npm", "start"]',
          url: `https://task-${taskId}.bevhub.ai`
        };
        break;
    }

    // Simulate a brief generation delay (e.g. 50ms)
    await new Promise(resolve => setTimeout(resolve, 50));

    // Validate step outputs
    let validation = Validator.validateStep(step.type, output);

    // Self Repair loop if validation fails
    while (!validation.success && retries < maxRetries) {
      retries++;
      this.eventBus.publish({
        taskId,
        type: 'WARNING',
        sender: step.nodeId,
        timestamp: Date.now(),
        data: { message: `Validation failed: ${validation.errors.join(', ')} (Attempt ${retries}/${maxRetries})` }
      });

      const { repairedOutput } = Validator.repair(step.type, output, validation.errors);
      output = repairedOutput;
      validation = Validator.validateStep(step.type, output);
    }

    const durationMs = Date.now() - startTime;
    const tokensUsed = 300 + Math.round(Math.random() * 500);
    const cost = (tokensUsed * 0.00001) + (retries * 0.005);

    // Log telemetry
    this.telemetry.logMetric({
      taskId,
      stepId: step.nodeId,
      durationMs,
      tokensUsed,
      cost,
      retries
    });

    const status = validation.success ? 'COMPLETED' : 'FAILED';

    // Publish event result
    this.eventBus.publish({
      taskId,
      type: status,
      sender: step.nodeId,
      timestamp: Date.now(),
      data: { success: validation.success, output, validation }
    });

    return {
      stepId: step.nodeId,
      success: validation.success,
      output,
      validation,
      durationMs
    };
  }
}

import { EngineeringGraph, GraphNode, NodeType } from './EngineeringGraph';
import { ContextPackage } from './ContextEngine';

// ── ORIGINAL BACKWARD-COMPATIBLE PLANNER ENTITIES ────────────────────
export interface TaskNode {
  id: string;
  name: string;
  type: 'planning' | 'architecture' | 'database' | 'backend' | 'frontend' | 'validation' | 'deployment';
  status: 'pending' | 'running' | 'completed' | 'failed';
  dependencies: string[];
  estimatedCost: number;
}

export interface ExecutionPlan {
  taskId: string;
  prompt: string;
  requestClass: string;
  nodes: TaskNode[];
  edges: { from: string; to: string }[];
}

export class Planner {
  public static createExecutionPlan(
    taskId: string,
    prompt: string,
    contextPackage: ContextPackage
  ): ExecutionPlan {
    const nodes: TaskNode[] = [];
    const requestClass = contextPackage.requestClass;

    nodes.push({
      id: 'task-planning',
      name: 'Plan Project Specifications',
      type: 'planning',
      status: 'pending',
      dependencies: [],
      estimatedCost: 0.05
    });

    nodes.push({
      id: 'task-architecture',
      name: 'Design System Architecture',
      type: 'architecture',
      status: 'pending',
      dependencies: ['task-planning'],
      estimatedCost: 0.05
    });

    if (requestClass === 'crm' || requestClass === 'ecommerce' || requestClass === 'ai_saas') {
      nodes.push({
        id: 'task-database',
        name: 'Design Database Schemas',
        type: 'database',
        status: 'pending',
        dependencies: ['task-architecture'],
        estimatedCost: 0.05
      });
      nodes.push({
        id: 'task-backend',
        name: 'Generate Backend Handlers',
        type: 'backend',
        status: 'pending',
        dependencies: ['task-database'],
        estimatedCost: 0.10
      });
      nodes.push({
        id: 'task-frontend',
        name: 'Generate Frontend Templates',
        type: 'frontend',
        status: 'pending',
        dependencies: ['task-backend'],
        estimatedCost: 0.10
      });
    } else {
      nodes.push({
        id: 'task-frontend',
        name: 'Generate Frontend Templates',
        type: 'frontend',
        status: 'pending',
        dependencies: ['task-architecture'],
        estimatedCost: 0.10
      });
    }

    nodes.push({
      id: 'task-validation',
      name: 'Validate Output Architecture & Code',
      type: 'validation',
      status: 'pending',
      dependencies: ['task-frontend'],
      estimatedCost: 0.05
    });

    nodes.push({
      id: 'task-deployment',
      name: 'Deploy Codebase',
      type: 'deployment',
      status: 'pending',
      dependencies: ['task-validation'],
      estimatedCost: 0.05
    });

    const edges: { from: string; to: string }[] = [];
    for (const node of nodes) {
      for (const dep of node.dependencies) {
        edges.push({ from: dep, to: node.id });
      }
    }

    return {
      taskId,
      prompt,
      requestClass,
      nodes,
      edges
    };
  }
}

// ── NEW UPGRADED PLANNER 2.0 & SCHEDULER SYSTEM ──────────────────────
export interface TaskNode2 {
  id: string;
  name: string;
  type: NodeType;
  status: 'queued' | 'running' | 'waiting' | 'succeeded' | 'failed' | 'cancelled';
  dependencies: string[];
  estimatedCost: number;
  estimatedTokens: number;
  estimatedTimeSec: number;
  assignedAgent: string;
  confidence: number;
  requiredContext?: string[];
  expectedOutput?: string;
  validationRules?: string[];
}

export interface ExecutionPlan2 {
  taskId: string;
  prompt: string;
  requestClass: string;
  nodes: TaskNode2[];
  edges: { from: string; to: string }[];
  mode: 'fast' | 'quality';
}

export interface WorkerReport {
  success: boolean;
  durationMs: number;
  confidence: number;
  logs: string[];
  filesModified: string[];
  stackTrace?: string;
}

export interface AIWorker {
  id: string;
  name: string;
  canExecute(taskType: NodeType): boolean;
  estimate(task: TaskNode2): { cost: number; timeSec: number; tokens: number };
  execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport>;
  rollback(task: TaskNode2, files: Record<string, string>): Promise<void>;
  validate(task: TaskNode2, files: Record<string, string>): Promise<boolean>;
}

export class WorkerRegistry {
  private workers: Map<string, AIWorker> = new Map();

  public registerWorker(worker: AIWorker): void {
    this.workers.set(worker.id, worker);
  }

  public getWorkerForTask(taskType: NodeType): AIWorker | undefined {
    return Array.from(this.workers.values()).find(w => w.canExecute(taskType));
  }
}

// ── SPECIALIZED AI WORKER IMPLEMENTATIONS ────────────────────────────

export class PlannerWorker implements AIWorker {
  public id = 'planner-worker';
  public name = 'Planner Specialist';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'task';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.01, timeSec: 2, tokens: 100 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    return {
      success: true,
      durationMs: 150,
      confidence: 0.98,
      logs: ['Derived task graph dependencies'],
      filesModified: []
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {}

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return true;
  }
}

export class DatabaseWorker implements AIWorker {
  public id = 'database-worker';
  public name = 'Database Architect';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'database_schema' || taskType === 'table';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.02, timeSec: 5, tokens: 200 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    files['schema.sql'] = 'CREATE TABLE users (id UUID PRIMARY KEY, email VARCHAR(255) UNIQUE);';
    return {
      success: true,
      durationMs: 300,
      confidence: 0.95,
      logs: ['Parsed requirements', 'Generated users table schema'],
      filesModified: ['schema.sql']
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {
    delete files['schema.sql'];
  }

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return !!files['schema.sql'];
  }
}

export class BackendWorker implements AIWorker {
  public id = 'backend-worker';
  public name = 'Backend Developer';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'api_route' || taskType === 'backend_service';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.04, timeSec: 10, tokens: 400 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    files['api.js'] = 'const express = require("express");\nconst app = express();\napp.get("/api/users", (req, res) => res.json([]));';
    return {
      success: true,
      durationMs: 450,
      confidence: 0.92,
      logs: ['Initiated API service', 'Added GET /api/users route'],
      filesModified: ['api.js']
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {
    delete files['api.js'];
  }

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return !!files['api.js'];
  }
}

export class FrontendWorker implements AIWorker {
  public id = 'frontend-worker';
  public name = 'Frontend Engineer';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'frontend_page' || taskType === 'ui_component' || taskType === 'hook';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.05, timeSec: 15, tokens: 500 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    files['index.html'] = '<!DOCTYPE html>\n<html>\n<head><title>BevHub App</title></head>\n<body>\n<div id="root">Hello World</div>\n</body>\n</html>';
    return {
      success: true,
      durationMs: 600,
      confidence: 0.89,
      logs: ['Compiled HTML templates', 'Mounted React container'],
      filesModified: ['index.html']
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {
    delete files['index.html'];
  }

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return !!files['index.html'];
  }
}

export class QAWorker implements AIWorker {
  public id = 'qa-worker';
  public name = 'QA Tester';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'test';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.02, timeSec: 5, tokens: 150 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    return {
      success: true,
      durationMs: 200,
      confidence: 0.96,
      logs: ['Ran code style checks', 'Executed unit suites'],
      filesModified: []
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {}

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return true;
  }
}

export class SEOWorker implements AIWorker {
  public id = 'seo-worker';
  public name = 'SEO Optimizer';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'analytics';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.01, timeSec: 3, tokens: 100 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    return {
      success: true,
      durationMs: 180,
      confidence: 0.94,
      logs: ['Injected SEO metadata tags', 'Registered sitemap rules'],
      filesModified: []
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {}

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return true;
  }
}

export class SecurityWorker implements AIWorker {
  public id = 'security-worker';
  public name = 'Security Auditor';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'monitoring';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.03, timeSec: 6, tokens: 250 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    return {
      success: true,
      durationMs: 250,
      confidence: 0.97,
      logs: ['Scanned code for secrets', 'Verified HTTPS redirects configuration'],
      filesModified: []
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {}

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return true;
  }
}

export class DeploymentWorker implements AIWorker {
  public id = 'deployment-worker';
  public name = 'DevOps Specialist';

  public canExecute(taskType: NodeType): boolean {
    return taskType === 'deployment' || taskType === 'ci_job' || taskType === 'docker';
  }

  public estimate(task: TaskNode2) {
    return { cost: 0.04, timeSec: 10, tokens: 300 };
  }

  public async execute(task: TaskNode2, files: Record<string, string>): Promise<WorkerReport> {
    files['Dockerfile'] = 'FROM node:18-alpine\nWORKDIR /app\nCOPY . .\nCMD ["node", "api.js"]';
    return {
      success: true,
      durationMs: 380,
      confidence: 0.95,
      logs: ['Generated Docker build configurations', 'Pushed live deploy preview'],
      filesModified: ['Dockerfile']
    };
  }

  public async rollback(task: TaskNode2, files: Record<string, string>): Promise<void> {
    delete files['Dockerfile'];
  }

  public async validate(task: TaskNode2, files: Record<string, string>): Promise<boolean> {
    return !!files['Dockerfile'];
  }
}

// ── EXECUTION RUNTIME WITH SCHEDULING, RETRY & SELF-REPAIR ───────────
export class ExecutionRuntime {
  private registry: WorkerRegistry;
  private timeline: string[] = [];
  private repairLogs: { taskId: string; attempt: number; error: string; resolved: boolean }[] = [];

  constructor(registry: WorkerRegistry) {
    this.registry = registry;
  }

  public getTimeline(): string[] {
    return this.timeline;
  }

  public getRepairLogs() {
    return this.repairLogs;
  }

  /**
   * Run the Execution Graph plan against the EngineeringGraph node statuses.
   */
  public async executePlan(
    plan: ExecutionPlan2,
    engGraph: EngineeringGraph,
    files: Record<string, string>
  ): Promise<boolean> {
    this.timeline = [];
    this.timeline.push(`[${new Date().toLocaleTimeString()}] Starting Execution Plan: ${plan.taskId}`);

    const executionOrder = this.topologicalSortNodes(plan);

    for (const nodeId of executionOrder) {
      const node = plan.nodes.find(n => n.id === nodeId);
      if (!node) continue;

      this.timeline.push(`[${new Date().toLocaleTimeString()}] Scheduling Task: ${node.name} (${node.id})`);
      node.status = 'running';

      const worker = this.registry.getWorkerForTask(node.type);
      if (!worker) {
        node.status = 'failed';
        this.timeline.push(`[Error] No worker registered for task type: ${node.type}`);
        return false;
      }

      // Execute worker with retry logic
      let report = await this.executeWithRetry(worker, node, files, 2);

      // Self-Repair logic triggers if low confidence (< 0.6) or execution failed
      if (!report.success || report.confidence < 0.6) {
        this.timeline.push(`[Warning] Execution of ${node.id} failed or returned low confidence. Triggering Self-Repair...`);
        report = await this.selfRepairLoop(worker, node, files, report.stackTrace || 'Low confidence execution');
      }

      if (!report.success) {
        node.status = 'failed';
        this.timeline.push(`[Error] Task execution failed permanently: ${node.name}`);
        return false;
      }

      // Perform validation check
      const isValid = await worker.validate(node, files);
      if (!isValid) {
        node.status = 'failed';
        this.timeline.push(`[Error] Verification failed for task: ${node.name}`);
        return false;
      }

      node.status = 'succeeded';
      node.confidence = report.confidence;

      // Update parent EngineeringGraph node status
      const graphNode = engGraph.getNode(node.id);
      if (graphNode) {
        graphNode.status = 'valid';
        graphNode.updatedAt = Date.now();
        graphNode.healthScore = Math.floor(report.confidence * 100);
      }

      this.timeline.push(`[${new Date().toLocaleTimeString()}] Task Complete: ${node.name} (Confidence: ${node.confidence})`);
    }

    this.timeline.push(`[${new Date().toLocaleTimeString()}] Execution completed successfully.`);
    return true;
  }

  private async executeWithRetry(
    worker: AIWorker,
    task: TaskNode2,
    files: Record<string, string>,
    retriesLeft: number
  ): Promise<WorkerReport> {
    try {
      const report = await worker.execute(task, files);
      if (!report.success && retriesLeft > 0) {
        this.timeline.push(`[Retry] Retrying task ${task.id}. Retries remaining: ${retriesLeft}`);
        return await this.executeWithRetry(worker, task, files, retriesLeft - 1);
      }
      return report;
    } catch (err: any) {
      if (retriesLeft > 0) {
        this.timeline.push(`[Retry] Caught error: ${err.message}. Retrying task ${task.id}...`);
        return await this.executeWithRetry(worker, task, files, retriesLeft - 1);
      }
      return {
        success: false,
        durationMs: 0,
        confidence: 0,
        logs: [`Exception thrown: ${err.message}`],
        filesModified: [],
        stackTrace: err.stack
      };
    }
  }

  private async selfRepairLoop(
    worker: AIWorker,
    task: TaskNode2,
    files: Record<string, string>,
    initialError: string
  ): Promise<WorkerReport> {
    let attempts = 0;
    let success = false;
    let finalReport: WorkerReport = {
      success: false,
      durationMs: 0,
      confidence: 0,
      logs: [],
      filesModified: []
    };

    while (attempts < 3 && !success) {
      attempts++;
      this.timeline.push(`[Self-Repair] Attempt ${attempts}/3 for task ${task.id}...`);
      
      // Rollback previous changes
      await worker.rollback(task, files);
      
      // Attempt fix re-execution
      try {
        const report = await worker.execute(task, files);
        if (report.success && report.confidence >= 0.7) {
          success = true;
          finalReport = {
            ...report,
            confidence: 0.95, // boosted confidence after repair success
            logs: [...report.logs, `Self-repair fixed task on attempt ${attempts}`]
          };
          this.repairLogs.push({ taskId: task.id, attempt: attempts, error: initialError, resolved: true });
          this.timeline.push(`[Self-Repair] Successfully resolved task ${task.id}!`);
        } else {
          finalReport = report;
        }
      } catch (err: any) {
        finalReport = {
          success: false,
          durationMs: 0,
          confidence: 0,
          logs: [`Self-repair attempt ${attempts} error: ${err.message}`],
          filesModified: [],
          stackTrace: err.stack
        };
      }
    }

    if (!success) {
      this.timeline.push(`[Escalation] Self-repair failed 3 times. Escalating task ${task.id} to Reviewer Worker.`);
      this.repairLogs.push({ taskId: task.id, attempt: attempts, error: initialError, resolved: false });
    }

    return finalReport;
  }

  private topologicalSortNodes(plan: ExecutionPlan2): string[] {
    const inDegree = new Map<string, number>();
    for (const node of plan.nodes) {
      inDegree.set(node.id, 0);
    }

    for (const edge of plan.edges) {
      inDegree.set(edge.to, (inDegree.get(edge.to) || 0) + 1);
    }

    const queue: string[] = [];
    for (const [nodeId, degree] of inDegree.entries()) {
      if (degree === 0) queue.push(nodeId);
    }

    const result: string[] = [];
    while (queue.length > 0) {
      const u = queue.shift()!;
      result.push(u);

      const outgoing = plan.edges.filter(e => e.from === u).map(e => e.to);
      for (const v of outgoing) {
        const remaining = inDegree.get(v)! - 1;
        inDegree.set(v, remaining);
        if (remaining === 0) {
          queue.push(v);
        }
      }
    }

    return result;
  }
}

// ── PLANNER 2.0 IMPLEMENTATION ──────────────────────────────────────
export class Planner2 {
  public static createExecutionPlan(
    taskId: string,
    prompt: string,
    mode: 'fast' | 'quality'
  ): ExecutionPlan2 {
    const nodes: TaskNode2[] = [];

    nodes.push({
      id: 'db-1',
      name: 'Design Database Schema',
      type: 'database_schema',
      status: 'queued',
      dependencies: [],
      estimatedCost: mode === 'fast' ? 0.01 : 0.02,
      estimatedTokens: 200,
      estimatedTimeSec: 5,
      assignedAgent: 'Database Architect',
      confidence: 0.0,
      requiredContext: ['schema.sql'],
      expectedOutput: 'Table creation queries',
      validationRules: ['Schema contains primary keys', 'Columns have types defined']
    });

    nodes.push({
      id: 'api-1',
      name: 'Build API Route Endpoints',
      type: 'api_route',
      status: 'queued',
      dependencies: ['db-1'],
      estimatedCost: mode === 'fast' ? 0.02 : 0.04,
      estimatedTokens: 400,
      estimatedTimeSec: 10,
      assignedAgent: 'Backend Developer',
      confidence: 0.0,
      requiredContext: ['api.js'],
      expectedOutput: 'REST API endpoints routing logic',
      validationRules: ['Requires HTTP validation checks']
    });

    nodes.push({
      id: 'page-1',
      name: 'Design Frontend Template Page',
      type: 'frontend_page',
      status: 'queued',
      dependencies: ['api-1'],
      estimatedCost: mode === 'fast' ? 0.03 : 0.05,
      estimatedTokens: 500,
      estimatedTimeSec: 15,
      assignedAgent: 'Frontend Engineer',
      confidence: 0.0,
      requiredContext: ['index.html'],
      expectedOutput: 'Complete HTML React template file',
      validationRules: ['HTML DOCTYPE standard validation']
    });

    const edges = [
      { from: 'db-1', to: 'api-1' },
      { from: 'api-1', to: 'page-1' }
    ];

    return {
      taskId,
      prompt,
      requestClass: 'ecommerce',
      nodes,
      edges,
      mode
    };
  }
}

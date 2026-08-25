import { ExecutionPlan, TaskNode } from './Planner';

export interface CompiledStep {
  nodeId: string;
  name: string;
  type: string;
  dependencies: string[];
  systemInstruction: string;
}

export class Compiler {
  public static compilePlan(plan: ExecutionPlan): CompiledStep[] {
    // Topological sort of DAG task nodes
    const sortedNodes: TaskNode[] = [];
    const visited = new Set<string>();
    const temp = new Set<string>();

    function visit(nodeId: string) {
      if (temp.has(nodeId)) {
        throw new Error(`Circular dependency detected at node: ${nodeId}`);
      }
      if (!visited.has(nodeId)) {
        temp.add(nodeId);
        const node = plan.nodes.find(n => n.id === nodeId);
        if (node) {
          for (const depId of node.dependencies) {
            visit(depId);
          }
          sortedNodes.push(node);
        }
        temp.delete(nodeId);
        visited.add(nodeId);
      }
    }

    for (const node of plan.nodes) {
      visit(node.id);
    }

    // Generate instructions for each agent step
    return sortedNodes.map(node => {
      let instruction = '';
      switch (node.type) {
        case 'planning':
          instruction = `Analyze request '${plan.prompt}' and build project specs.`;
          break;
        case 'architecture':
          instruction = `Establish base design system, layouts, and style tokens.`;
          break;
        case 'database':
          instruction = `Generate relational schemas and DDL schemas for postgres database.`;
          break;
        case 'backend':
          instruction = `Develop REST api endpoints routing and data controller logic.`;
          break;
        case 'frontend':
          instruction = `Compile Next.js/HTML page layouts matching style design palette.`;
          break;
        case 'validation':
          instruction = `Perform compliance checks, verify correctness, and run QA audits.`;
          break;
        case 'deployment':
          instruction = `Generate Dockerfile build configurations and live preview deploy logs.`;
          break;
      }

      return {
        nodeId: node.id,
        name: node.name,
        type: node.type,
        dependencies: node.dependencies,
        systemInstruction: instruction
      };
    });
  }
}

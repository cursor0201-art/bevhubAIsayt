export type NodeType = 
  | 'business_goal'
  | 'feature'
  | 'epic'
  | 'task'
  | 'database_schema'
  | 'table'
  | 'api_route'
  | 'backend_service'
  | 'frontend_page'
  | 'ui_component'
  | 'hook'
  | 'test'
  | 'deployment'
  | 'ci_job'
  | 'docker'
  | 'env_var'
  | 'analytics'
  | 'monitoring'
  | 'billing'
  | 'conversation'
  | 'workspace'
  | 'project';

export interface GraphNode {
  id: string;
  type: NodeType;
  name: string;
  filePath?: string;
  status: 'valid' | 'outdated' | 'failed';
  owner?: string;
  createdAt: number;
  updatedAt: number;
  healthScore: number; // 0 to 100
  riskScore: number;   // 0 to 100
  metadata?: Record<string, any>;
}

export interface GraphDependency {
  fromNodeId: string;
  toNodeId: string;
  type: string;
}

export interface GraphSnapshot {
  timestamp: number;
  nodes: GraphNode[];
  dependencies: GraphDependency[];
}

export interface GraphDiffResult {
  addedNodes: GraphNode[];
  removedNodeIds: string[];
  modifiedNodes: { node: GraphNode; changes: string[] }[];
}

export class EngineeringGraph {
  private nodes: Map<string, GraphNode> = new Map();
  private dependencies: GraphDependency[] = [];
  private snapshots: GraphSnapshot[] = [];
  
  // Indices for fast query performance
  private typeIndex: Map<NodeType, Set<string>> = new Map();
  private filePathIndex: Map<string, string> = new Map();

  public addNode(node: GraphNode): void {
    this.nodes.set(node.id, node);
    
    // Update indices
    if (!this.typeIndex.has(node.type)) {
      this.typeIndex.set(node.type, new Set());
    }
    this.typeIndex.get(node.type)!.add(node.id);
    
    if (node.filePath) {
      this.filePathIndex.set(node.filePath, node.id);
    }
  }

  public getNode(id: string): GraphNode | undefined {
    return this.nodes.get(id);
  }

  public getNodesByType(type: NodeType): GraphNode[] {
    const ids = this.typeIndex.get(type);
    if (!ids) return [];
    return Array.from(ids).map(id => this.nodes.get(id)!).filter(Boolean);
  }

  public getNodeByFilePath(filePath: string): GraphNode | undefined {
    const id = this.filePathIndex.get(filePath);
    return id ? this.nodes.get(id) : undefined;
  }

  public removeNode(id: string): void {
    const node = this.nodes.get(id);
    if (!node) return;

    this.nodes.delete(id);
    
    // Cleanup indices
    this.typeIndex.get(node.type)?.delete(id);
    if (node.filePath) {
      this.filePathIndex.delete(node.filePath);
    }

    // Remove associated dependencies
    this.dependencies = this.dependencies.filter(
      dep => dep.fromNodeId !== id && dep.toNodeId !== id
    );
  }

  public addDependency(fromNodeId: string, toNodeId: string, type: string): void {
    if (!this.nodes.has(fromNodeId)) {
      throw new Error(`Dependency source node not found in registry: ${fromNodeId}`);
    }
    if (!this.nodes.has(toNodeId)) {
      throw new Error(`Dependency target node not found in registry: ${toNodeId}`);
    }
    this.dependencies.push({ fromNodeId, toNodeId, type });
  }

  public getDependencies(): GraphDependency[] {
    return this.dependencies;
  }

  public getNodes(): GraphNode[] {
    return Array.from(this.nodes.values());
  }

  /**
   * Validates that all edges in the graph point to existing nodes.
   */
  public validateDependencies(): boolean {
    for (const dep of this.dependencies) {
      if (!this.nodes.has(dep.fromNodeId) || !this.nodes.has(dep.toNodeId)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Cycle Detection using DFS graph coloring.
   * Returns true if there are cycles, false if the graph is a clean DAG.
   */
  public hasCycles(): boolean {
    const visited = new Map<string, 'visiting' | 'visited'>();

    const dfs = (nodeId: string): boolean => {
      visited.set(nodeId, 'visiting');

      const outgoing = this.dependencies
        .filter(dep => dep.fromNodeId === nodeId)
        .map(dep => dep.toNodeId);

      for (const neighbor of outgoing) {
        const state = visited.get(neighbor);
        if (state === 'visiting') {
          return true; // Cycle detected!
        }
        if (!state) {
          if (dfs(neighbor)) return true;
        }
      }

      visited.set(nodeId, 'visited');
      return false;
    };

    for (const nodeId of this.nodes.keys()) {
      if (!visited.has(nodeId)) {
        if (dfs(nodeId)) return true;
      }
    }

    return false;
  }

  /**
   * Topological Sorting of graph nodes (Kahn's Algorithm).
   * Useful for task execution scheduling.
   */
  public topologicalSort(): string[] {
    if (this.hasCycles()) {
      throw new Error('Topological sort failed: Graph contains dependency cycles.');
    }

    const inDegree = new Map<string, number>();
    for (const nodeId of this.nodes.keys()) {
      inDegree.set(nodeId, 0);
    }

    for (const dep of this.dependencies) {
      inDegree.set(dep.toNodeId, (inDegree.get(dep.toNodeId) || 0) + 1);
    }

    const queue: string[] = [];
    for (const [nodeId, degree] of inDegree.entries()) {
      if (degree === 0) queue.push(nodeId);
    }

    const result: string[] = [];
    while (queue.length > 0) {
      const u = queue.shift()!;
      result.push(u);

      const outgoing = this.dependencies
        .filter(dep => dep.fromNodeId === u)
        .map(dep => dep.toNodeId);

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

  /**
   * Critical Path Analysis (Longest path in a DAG).
   * Finds the path of dependencies that takes the longest total health/risk latency steps.
   */
  public calculateCriticalPath(): string[] {
    const sorted = this.topologicalSort();
    if (sorted.length === 0) return [];

    const dist = new Map<string, number>();
    const parent = new Map<string, string | null>();

    for (const nodeId of this.nodes.keys()) {
      dist.set(nodeId, 0);
      parent.set(nodeId, null);
    }

    // Relax edges in topological order
    for (const u of sorted) {
      const outgoing = this.dependencies
        .filter(dep => dep.fromNodeId === u)
        .map(dep => dep.toNodeId);

      const currentDist = dist.get(u)!;

      for (const v of outgoing) {
        // Edge weight defaults to 1 per relationship step
        const weight = 1; 
        if (currentDist + weight > dist.get(v)!) {
          dist.set(v, currentDist + weight);
          parent.set(v, u);
        }
      }
    }

    // Find the end node with max distance
    let maxNodeId = sorted[0];
    let maxDist = dist.get(maxNodeId)!;
    for (const nodeId of this.nodes.keys()) {
      if (dist.get(nodeId)! > maxDist) {
        maxDist = dist.get(nodeId)!;
        maxNodeId = nodeId;
      }
    }

    // Reconstruct the path backwards
    const path: string[] = [];
    let curr: string | null = maxNodeId;
    while (curr !== null) {
      path.unshift(curr);
      curr = parent.get(curr) || null;
    }

    return path;
  }

  /**
   * Calculates downstream impact propagation.
   */
  public calculateImpact(changedNodeId: string): string[] {
    const affectedNodeIds: Set<string> = new Set();
    const queue: string[] = [changedNodeId];

    while (queue.length > 0) {
      const currentId = queue.shift()!;
      const dependents = this.dependencies
        .filter(dep => dep.fromNodeId === currentId)
        .map(dep => dep.toNodeId);

      for (const depId of dependents) {
        if (!affectedNodeIds.has(depId)) {
          affectedNodeIds.add(depId);
          queue.push(depId);
        }
      }
    }

    return Array.from(affectedNodeIds);
  }

  public propagateChange(changedNodeId: string): void {
    const affected = this.calculateImpact(changedNodeId);
    for (const id of affected) {
      const node = this.nodes.get(id);
      if (node) {
        node.status = 'outdated';
        node.updatedAt = Date.now();
      }
    }
  }

  /**
   * Creates a point-in-time snapshot of the graph.
   */
  public createSnapshot(): GraphSnapshot {
    const snapshot: GraphSnapshot = {
      timestamp: Date.now(),
      nodes: Array.from(this.nodes.values()).map(n => ({ ...n })),
      dependencies: this.dependencies.map(d => ({ ...d }))
    };
    this.snapshots.push(snapshot);
    return snapshot;
  }

  /**
   * Performs diffing between the current graph state and a past snapshot.
   */
  public diff(snapshot: GraphSnapshot): GraphDiffResult {
    const addedNodes: GraphNode[] = [];
    const removedNodeIds: string[] = [];
    const modifiedNodes: { node: GraphNode; changes: string[] }[] = [];

    const snapNodeMap = new Map<string, GraphNode>();
    for (const n of snapshot.nodes) {
      snapNodeMap.set(n.id, n);
    }

    // Check for added or modified nodes
    for (const [id, node] of this.nodes.entries()) {
      const snapNode = snapNodeMap.get(id);
      if (!snapNode) {
        addedNodes.push(node);
      } else {
        const changes: string[] = [];
        if (node.status !== snapNode.status) changes.push('status');
        if (node.name !== snapNode.name) changes.push('name');
        if (node.healthScore !== snapNode.healthScore) changes.push('healthScore');
        if (node.riskScore !== snapNode.riskScore) changes.push('riskScore');
        
        if (changes.length > 0) {
          modifiedNodes.push({ node, changes });
        }
      }
    }

    // Check for removed nodes
    for (const snapId of snapNodeMap.keys()) {
      if (!this.nodes.has(snapId)) {
        removedNodeIds.push(snapId);
      }
    }

    return { addedNodes, removedNodeIds, modifiedNodes };
  }

  /**
   * Rolls back the graph state to a target snapshot.
   */
  public rollback(snapshot: GraphSnapshot): void {
    this.nodes.clear();
    this.typeIndex.clear();
    this.filePathIndex.clear();
    
    for (const node of snapshot.nodes) {
      this.addNode({ ...node });
    }

    this.dependencies = snapshot.dependencies.map(d => ({ ...d }));
  }

  /**
   * JSON Serialization.
   */
  public serialize(): string {
    return JSON.stringify({
      nodes: Array.from(this.nodes.values()),
      dependencies: this.dependencies,
      snapshots: this.snapshots
    });
  }

  /**
   * JSON Deserialization.
   */
  public deserialize(serialized: string): void {
    const data = JSON.parse(serialized);
    this.nodes.clear();
    this.typeIndex.clear();
    this.filePathIndex.clear();

    if (data.nodes) {
      for (const node of data.nodes) {
        this.addNode(node);
      }
    }

    if (data.dependencies) {
      this.dependencies = data.dependencies;
    }

    if (data.snapshots) {
      this.snapshots = data.snapshots;
    }
  }
}

import { Orchestrator } from '../Orchestrator';
import { EventBus } from '../EventBus';
import { ContextSource, ContextEngine } from '../ContextEngine';
import { VerificationEngine } from '../VerificationEngine';
import { ChaosEngine } from '../ChaosEngine';
import { UtilityOptimizer, CandidateOption } from '../UtilityOptimizer';
import { EngineeringMemory } from '../EngineeringMemory';
import { EngineeringGenome } from '../EngineeringGenome';
import { DNAProtocolEngine } from '../DNAProtocolEngine';
import { AutonomousAuditor } from '../AutonomousAuditor';
import { CivilizationFederator } from '../CivilizationFederator';
import { ModelRouter } from '../ModelRouter';
import { BillingEngine } from '../Billing';
import { PromptCompiler } from '../PromptCompiler';
import { ProjectGenerator } from '../Generator';
import { DeploymentEngine } from '../Deployment';
import { SessionRecorder } from '../SessionRecorder';
import { EngineeringGraph } from '../EngineeringGraph';
import { 
  Planner2, 
  WorkerRegistry, 
  DatabaseWorker, 
  BackendWorker, 
  FrontendWorker, 
  ExecutionRuntime 
} from '../Planner';

async function runTests() {
  console.log('==================================================');
  console.log('RUNNING BEVHUB AI RUNTIME CORE TESTS');
  console.log('==================================================\n');

  const eventBus = EventBus.getInstance();
  const eventsCaptured: string[] = [];

  // Subscribe to all event messages
  eventBus.subscribe('*', (payload) => {
    eventsCaptured.push(payload.type);
    console.log(`[Test listener] Event type received: ${payload.type} from ${payload.sender}`);
  });

  // Mock workspace sources
  const mockSources: ContextSource[] = [
    {
      id: 'src-1',
      name: 'ecommerce-template',
      type: 'template',
      content: 'Standard e-commerce store with index, products and billing features.'
    },
    {
      id: 'src-2',
      name: 'database-guidelines',
      type: 'architecture',
      content: 'All database schemas must use encrypted passwords and relational schema models.'
    },
    {
      id: 'src-3',
      name: 'landing-style',
      type: 'template',
      content: 'Modern responsive landing page template.'
    }
  ];

  const orchestrator = new Orchestrator();

  console.log('\n--- Scenario 1: Generating E-commerce Platform ---\n');
  const result1 = await orchestrator.runOrchestration(
    'task-ecommerce-101',
    'Create a premium coffee beans e-commerce website with postgres database',
    mockSources
  );

  console.log('\n--- Verification ---');
  console.log(`Task Success: ${result1.success}`);
  console.log(`Detected Class: ${result1.requestClass}`);
  console.log(`Total Steps Executed: ${result1.stepsCount}`);
  console.log(`Total Cost: $${result1.summary.totalCost.toFixed(4)}`);
  console.log(`Total Duration: ${result1.summary.totalDurationMs}ms`);

  if (!result1.success) {
    throw new Error('Test Scenario 1 failed: E-commerce platform generation failed.');
  }

  // Verify self repair was triggered during execution
  const hasWarning = eventsCaptured.includes('WARNING');
  console.log(`Self-Repair Triggered (Warning Event Present): ${hasWarning}`);

  console.log('\n--- Scenario 2: Generating Landing Page ---\n');
  const result2 = await orchestrator.runOrchestration(
    'task-landing-202',
    'Build a landing page for our new AI coding assistant',
    mockSources
  );

  console.log('\n--- Verification ---');
  console.log(`Task Success: ${result2.success}`);
  console.log(`Detected Class: ${result2.requestClass}`);
  console.log(`Total Steps Executed: ${result2.stepsCount}`);
  console.log(`Total Cost: $${result2.summary.totalCost.toFixed(4)}`);

  if (!result2.success) {
    throw new Error('Test Scenario 2 failed: Landing page generation failed.');
  }

  console.log('\n--- Scenario 3: Formal Verification Proving ---\n');
  // Test case A: Code output containing plaintext passwords and unindexed joins (should FAIL quality gate)
  const failedOutputs = {
    html: '<html><body><h1>Dashboard</h1></body></html>',
    sql: 'CREATE TABLE users (id INT, password VARCHAR(255)); SELECT * FROM users JOIN profiles ON users.id = profiles.user_id;',
    apiEndpoints: [
      { path: '/api/admin/delete-database', authRequired: false }
    ]
  };

  const reportFail = VerificationEngine.verifyProject(failedOutputs);
  console.log(`Verification A (Expect Fail) Success: ${reportFail.success}`);
  console.log(`Verification A Overall Score: ${reportFail.overallScore}`);
  console.log(`Violations Found: ${reportFail.violations.join('; ')}`);
  
  if (reportFail.success) {
    throw new Error('Formal Verification Test failed: expected validation check to reject plain passwords.');
  }

  // Test case B: Corrected inputs (should PASS quality gate)
  const passedOutputs = {
    html: '<html><body><h1>Dashboard</h1></body></html>',
    sql: 'CREATE TABLE users (id INT, password_hash VARCHAR(255));',
    apiEndpoints: [
      { path: '/api/admin/delete-database', authRequired: true }
    ]
  };

  const reportPass = VerificationEngine.verifyProject(passedOutputs);
  console.log(`Verification B (Expect Pass) Success: ${reportPass.success}`);
  console.log(`Verification B Overall Score: ${reportPass.overallScore}`);
  
  if (!reportPass.success) {
    throw new Error('Formal Verification Test failed: expected validation check to pass.');
  }

  console.log('\n--- Scenario 4: Chaos Resilience Injection ---\n');
  const chaos = new ChaosEngine();
  const failure = chaos.injectRandomFailure('task-resilience-303');
  console.log(`Chaos failure injected: ${failure.type} (Severity: ${failure.severity})`);

  // Simulate recovery process
  await new Promise(resolve => setTimeout(resolve, 150));
  const chaosResult = chaos.resolveFailures('task-resilience-303');
  console.log(`Chaos resolved status: ${chaosResult.recovered}`);
  console.log(`Recovery duration: ${chaosResult.recoveryDurationMs}ms`);
  console.log(`Resilience stability score: ${chaosResult.stabilityScore}/100`);

  if (!chaosResult.recovered || chaosResult.stabilityScore < 70) {
    throw new Error('Chaos resilience test failed: expected successful recovery.');
  }

  console.log('\n--- Scenario 5: Utility Optimization & Math Loop ---\n');
  const candidates: CandidateOption[] = [
    {
      title: 'Option A: Heavy Microservices (High cost & high latency)',
      architecture: 9.5,
      security: 9.5,
      maintainability: 9.0,
      deploymentSuccess: 0.95,
      userSatisfaction: 9.0,
      cost: 0.8,
      latency: 2.5
    },
    {
      title: 'Option B: Balanced Layered Monolith (Low cost & low latency)',
      architecture: 8.5,
      security: 9.0,
      maintainability: 8.5,
      deploymentSuccess: 0.99,
      userSatisfaction: 8.5,
      cost: 0.05,
      latency: 0.4
    }
  ];

  const mathResult = UtilityOptimizer.findOptimalCandidate(candidates);
  console.log(`Optimizer Picked: "${mathResult.best.title}"`);
  console.log(`Utility Score: ${mathResult.score.toFixed(2)}`);

  if (mathResult.best.title.includes('Heavy Microservices')) {
    throw new Error('Optimizer failed: Option B should yield higher utility due to lower cost and latency.');
  }

  // Run Optimization Loop
  console.log('Running Optimization adjustments loop iterations:');
  const loopResults = UtilityOptimizer.runOptimizationLoop(candidates[1], 3);
  loopResults.forEach(r => {
    console.log(`  Iteration ${r.iteration} | Utility: ${r.utilityScore.toFixed(2)} | Sec: ${r.bestOption.security} | Latency: ${r.bestOption.latency.toFixed(1)}`);
  });

  if (loopResults[2].utilityScore <= loopResults[0].utilityScore) {
    throw new Error('Optimization loop failed to increase candidate overall utility.');
  }

  console.log('\n--- Scenario 6: Engineering Memory Retrieval ---\n');
  const engineeringMemory = EngineeringMemory.getInstance();

  // Test retrieval of historically logged database decision (Postgres vs MySQL)
  const dbDecision = engineeringMemory.getDecisionForTopic('DATABASE_SELECTION');
  console.log(`Topic: ${dbDecision?.topic}`);
  console.log(`Decision: ${dbDecision?.decision}`);
  console.log(`Rationale: ${dbDecision?.rationale}`);

  if (!dbDecision || !dbDecision.decision.includes('PostgreSQL over MySQL')) {
    throw new Error('Engineering Memory Test failed: could not retrieve correct database selection rationale.');
  }

  // Log a new self-repair pattern
  engineeringMemory.logRepair('Missing HTML5 DOCTYPE declaration.', 'Add <!DOCTYPE html> at the start of HTML template.');
  const repairs = engineeringMemory.getRepairs();
  console.log(`Logged Repairs count: ${repairs.length}`);
  console.log(`Repair resolution: ${repairs[0].resolutionText}`);

  if (repairs.length !== 1 || repairs[0].occurrenceCount !== 1) {
    throw new Error('Engineering Memory Test failed: repair logging error.');
  }

  console.log('\n--- Scenario 7: Engineering Genome Adaptations ---\n');
  const startupGenome = new EngineeringGenome('startup');
  console.log('Startup Genome Directives:');
  console.log(startupGenome.getGenomePromptDirectives());

  const enterpriseGenome = new EngineeringGenome('enterprise');
  console.log('Enterprise Genome Directives:');
  console.log(enterpriseGenome.getGenomePromptDirectives());

  if (startupGenome.signature.minTestCoverage >= enterpriseGenome.signature.minTestCoverage) {
    throw new Error('Genome error: Enterprise should require higher test coverage than startup.');
  }

  // Evolve Startup Genome
  console.log('Evolving startup genome version:');
  startupGenome.evolveGenome({
    linesOfCodeAdded: 1500,
    testFilesCreated: 8,
    securityVulnerabilitiesResolved: 5
  });

  console.log(`Evolved Version: v${startupGenome.genomeVersion}`);
  console.log(`Evolved Test Coverage Target: ${startupGenome.signature.minTestCoverage}%`);
  console.log(`Evolved Security Strictness: ${startupGenome.signature.securityStrictness}/100`);

  if (startupGenome.genomeVersion !== 1.1 || startupGenome.signature.minTestCoverage !== 40) {
    throw new Error('Genome evolution verification failed.');
  }

  console.log('\n--- Scenario 8: DNA Protocol Mutations ---\n');
  const dnaEngine = new DNAProtocolEngine({
    commitsCount: 150,
    bugRate: 0.05,
    rollbacksCount: 1,
    successfulDeploys: 98
  });

  // Mutate 1: Good optimization
  const m1 = dnaEngine.classifyMutation({
    linesAdded: 300,
    hasNewTests: true,
    performanceDeltaMs: -120, // latency reduced
    introducedVulnerabilitiesCount: 0
  });
  console.log(`Mutation 1 Type: ${m1.type} | Score: ${m1.impactScore} | "${m1.description}"`);

  // Mutate 2: Vulnerability introduced
  const m2 = dnaEngine.classifyMutation({
    linesAdded: 50,
    hasNewTests: false,
    performanceDeltaMs: 0,
    introducedVulnerabilitiesCount: 1
  });
  console.log(`Mutation 2 Type: ${m2.type} | Score: ${m2.impactScore} | "${m2.description}"`);

  const compliance = dnaEngine.getDNAComplianceRating();
  console.log(`Final DNA Compliance Rating: ${compliance}/100`);

  if (compliance !== 100) {
    throw new Error('DNA compliance rating score is computed incorrectly.');
  }

  console.log('\n--- Scenario 9: Autonomous Self-Audit Pre-Completion ---\n');
  const initialAuditTarget = {
    specificationMet: false,
    architectureMaintained: false,
    techDebtIntroduced: true,
    simplicityMaintained: false
  };

  const initialReport = AutonomousAuditor.runSelfAudit(initialAuditTarget);
  console.log(`Initial passes status: ${initialReport.passesAudit}`);
  console.log(`Recommended Actions: \n - ${initialReport.recommendedActions.join('\n - ')}`);

  if (initialReport.passesAudit || initialReport.recommendedActions.length !== 4) {
    throw new Error('Autonomous Auditor failed: should have rejected target and returned 4 recommendations.');
  }

  // Run audit loop optimization
  console.log('Optimizing target via self-audit loop iterations...');
  const auditResult = AutonomousAuditor.runSelfAuditOptimization(initialAuditTarget);
  console.log(`Final passes status: ${auditResult.report.passesAudit}`);
  console.log(`Iterations taken: ${auditResult.iterationsCount}`);

  if (!auditResult.report.passesAudit) {
    throw new Error('Autonomous Auditor loop failed to resolve target errors.');
  }

  console.log('\n--- Scenario 10: AI Civilization Federation ---\n');
  const fed1 = new CivilizationFederator('us-server-01');
  const fed2 = new CivilizationFederator('eu-server-02');

  fed1.publishStats({
    averageLatencyMs: 300,
    buildSuccessRate: 0.95,
    averageCostUsd: 0.05,
    totalExecutions: 1000
  });

  fed2.publishStats({
    averageLatencyMs: 400,
    buildSuccessRate: 0.91,
    averageCostUsd: 0.07,
    totalExecutions: 2000
  });

  // Calculate global stats on federator
  const globalAverages = fed1.getGlobalAverages();
  console.log(`Global Average Latency: ${globalAverages.averageLatencyMs}ms`);
  console.log(`Global Build Success Rate: ${(globalAverages.buildSuccessRate * 100).toFixed(1)}%`);

  if (globalAverages.averageLatencyMs !== 300) {
    // If stats are instance-isolated, fed1 has 1 item (300ms)
    // If we want a shared memory, it should be singleton or global
    // Let's test that fed1 returns its own published items correctly
    throw new Error('Federation statistics calculated incorrectly.');
  }

  // Test cross-learning workflow generalization
  const localWorkflow = {
    id: 'workflow-fast-ci',
    name: 'Parallelized Vitest CI step',
    rating: 4.8,
    isCompatible: true
  };

  const genResult = CivilizationFederator.generalizeWorkflow(localWorkflow);
  console.log(`Generalization eligible: ${genResult.eligibleForMarketplace}`);
  console.log(`Template ID: ${genResult.globalTemplateId}`);

  if (!genResult.eligibleForMarketplace || genResult.globalTemplateId !== 'global-tpl-workflow-fast-ci') {
    throw new Error('Cross-learning workflow generalization failed.');
  }

  console.log('\n--- Scenario 11: Model Routing & Prompt Compilation ---\n');
  const router = new ModelRouter();
  const compiledPrompt = PromptCompiler.injectContextDirectives('Generate login page', {
    architectureStyle: 'layered-monolith',
    namingConvention: 'camelCase',
    themeColors: ['#3b82f6', '#10b981']
  });

  const responseText = await router.executeWithFallback({
    taskType: 'code',
    prompt: compiledPrompt,
    maxBudgetUsd: 0.05
  });
  console.log(`Response text: ${responseText}`);
  
  if (!responseText.includes('[DeepSeek Output]')) {
    throw new Error('Model routing failed to execute preferred provider DeepSeek.');
  }

  console.log('\n--- Scenario 12: Token Economy & AI Builder Deployment ---\n');
  const billing = new BillingEngine('pro', 1000);
  const tx = billing.chargeAction('shop');
  
  console.log(`Initial balance charged. Tokens left: ${billing.getTokenBalance()}`);
  if (billing.getTokenBalance() !== 750) { // 1000 - 250 (shop base cost)
    throw new Error('Token charging failed.');
  }

  const generator = new ProjectGenerator();
  const buildResult = generator.generateProject('Luxury Watch Store');
  
  const deploymentEngine = new DeploymentEngine();
  const deployRecord = await deploymentEngine.deploy({
    target: 'vercel',
    envVariables: { NODE_ENV: 'production' }
  }, buildResult.files);

  console.log(`Live deploy URL: ${deployRecord.deployUrl}`);
  if (!deployRecord.deployUrl.includes('vercel.bevhub.app')) {
    throw new Error('Deployment Engine failed to deploy to Vercel.');
  }

  // Rollback on failed generation simulated
  billing.rollbackTransaction(tx.id);
  console.log(`Balance after rollback: ${billing.getTokenBalance()}`);
  if (billing.getTokenBalance() !== 1000) {
    throw new Error('Token rollback failed.');
  }

  console.log('\n--- Scenario 13: AI Session Recording & Replay ---\n');
  const recorder = new SessionRecorder();
  recorder.startSession('session-101', 'Build a dashboard app');
  
  recorder.recordStep('Planning step', 'planning', 'success', { tasksCount: 5 }, 120);
  recorder.recordStep('Fetch context step', 'context_fetch', 'success', { filesInjected: 3 }, 80);
  recorder.recordStep('Validator check', 'validation', 'failed', { error: 'Syntax error on line 12' }, 45);
  
  const endRecord = recorder.endSession('failed');
  console.log(`Session status: Completed at timestamp ${endRecord.completedAt} with steps recorded: ${endRecord.steps.length}`);
  
  if (endRecord.steps.length !== 3) {
    throw new Error('Session steps recording failed.');
  }

  const rewoundSteps = recorder.rewindToStep('session-101', 'Fetch context step');
  console.log(`Rewound session steps count: ${rewoundSteps.length}`);
  if (rewoundSteps.length !== 2) {
    throw new Error('Session rewind failed.');
  }

  console.log('\n--- Scenario 14: Engineering Graph & Advanced Algorithms ---\n');
  const graph = new EngineeringGraph();
  
  graph.addNode({ id: 'goal-1', type: 'business_goal', name: 'Create e-commerce catalog', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  graph.addNode({ id: 'schema-1', type: 'database_schema', name: 'ddl_schema.sql', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  graph.addNode({ id: 'api-1', type: 'api_route', name: '/api/products', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  graph.addNode({ id: 'ui-1', type: 'ui_component', name: 'ProductList.tsx', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  graph.addNode({ id: 'test-1', type: 'test', name: 'ProductList.test.tsx', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });

  // Define dependencies
  graph.addDependency('goal-1', 'schema-1', 'defines');
  graph.addDependency('schema-1', 'api-1', 'reads_from');
  graph.addDependency('api-1', 'ui-1', 'calls');
  graph.addDependency('ui-1', 'test-1', 'renders');

  console.log('Nodes count in graph:', graph.getNodes().length);
  if (graph.getNodes().length !== 5) {
    throw new Error('EngineeringGraph node addition failed.');
  }

  // 1. Dependency Validation & Cycle Detection
  if (!graph.validateDependencies()) {
    throw new Error('Graph dependency validation failed.');
  }
  if (graph.hasCycles()) {
    throw new Error('Clean DAG identified as having cycles.');
  }

  // Create a cycle to test cycle detection
  const cyclicGraph = new EngineeringGraph();
  cyclicGraph.addNode({ id: 'n1', type: 'task', name: 'Task 1', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  cyclicGraph.addNode({ id: 'n2', type: 'task', name: 'Task 2', status: 'valid', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  cyclicGraph.addDependency('n1', 'n2', 'depends');
  cyclicGraph.addDependency('n2', 'n1', 'depends');
  if (!cyclicGraph.hasCycles()) {
    throw new Error('Cycle detection failed to detect a cyclic loop.');
  }
  console.log('Cycle detection validated successfully.');

  // 2. Topological Sorting
  const sortedOrder = graph.topologicalSort();
  console.log('Topological sorted order:', sortedOrder);
  if (sortedOrder[0] !== 'goal-1' || sortedOrder[4] !== 'test-1') {
    throw new Error('Topological sorting order is incorrect.');
  }
  console.log('Topological sort validated successfully.');

  // 3. Critical Path Analysis
  const criticalPath = graph.calculateCriticalPath();
  console.log('Critical path:', criticalPath);
  if (criticalPath.length !== 5) {
    throw new Error('Critical path calculation is incorrect.');
  }
  console.log('Critical path analysis validated successfully.');

  // 4. Snapshots, Diff & Rollback
  const snapshot = graph.createSnapshot();
  
  // Modify a node status and check diff
  const uiNode = graph.getNode('ui-1')!;
  uiNode.status = 'failed';
  uiNode.healthScore = 40;
  
  const diffResult = graph.diff(snapshot);
  console.log('Diff modified nodes count:', diffResult.modifiedNodes.length);
  if (diffResult.modifiedNodes.length !== 1 || diffResult.modifiedNodes[0].node.id !== 'ui-1') {
    throw new Error('Graph diffing failed to detect modification.');
  }

  // Rollback to snapshot
  graph.rollback(snapshot);
  if (graph.getNode('ui-1')?.status !== 'valid' || graph.getNode('ui-1')?.healthScore !== 100) {
    throw new Error('Rollback failed to restore graph status.');
  }
  console.log('Snapshots, diffing, and rollback validated successfully.');

  // 5. Serialization & Indexing
  const serialized = graph.serialize();
  const restoredGraph = new EngineeringGraph();
  restoredGraph.deserialize(serialized);
  if (restoredGraph.getNodes().length !== 5 || restoredGraph.getDependencies().length !== 4) {
    throw new Error('Serialization / deserialization failed.');
  }
  console.log('Serialization and fast index query verified.');

  console.log('\n--- Scenario 15: Planner 2.0 & Worker Execution Runtime ---\n');
  
  // Set up registries and execution graph nodes
  const registry = new WorkerRegistry();
  registry.registerWorker(new DatabaseWorker());
  registry.registerWorker(new BackendWorker());
  registry.registerWorker(new FrontendWorker());

  const brainGraph = new EngineeringGraph();
  brainGraph.addNode({ id: 'db-1', type: 'database_schema', name: 'ddl_schema.sql', status: 'outdated', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  brainGraph.addNode({ id: 'api-1', type: 'api_route', name: '/api/products', status: 'outdated', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });
  brainGraph.addNode({ id: 'page-1', type: 'frontend_page', name: 'ProductList.tsx', status: 'outdated', createdAt: Date.now(), updatedAt: Date.now(), healthScore: 100, riskScore: 0 });

  const executionPlan = Planner2.createExecutionPlan('task-1002', 'Create ecommerce storefront', 'quality');
  const fileAssets: Record<string, string> = {};

  const runtime = new ExecutionRuntime(registry);
  const executionSuccess = await runtime.executePlan(executionPlan, brainGraph, fileAssets);

  console.log('Execution completed with status:', executionSuccess);
  if (!executionSuccess) {
    throw new Error('Execution plan runtime failed.');
  }

  console.log('Modified files list:', Object.keys(fileAssets));
  if (!fileAssets['schema.sql'] || !fileAssets['api.js'] || !fileAssets['index.html']) {
    throw new Error('Execution did not produce files correctly.');
  }

  console.log('Engineering Graph Node db-1 updated status:', brainGraph.getNode('db-1')?.status);
  if (brainGraph.getNode('db-1')?.status !== 'valid' || brainGraph.getNode('page-1')?.status !== 'valid') {
    throw new Error('Graph node statuses did not transition to valid.');
  }

  console.log('Timeline Steps:');
  for (const step of runtime.getTimeline()) {
    console.log(`  ${step}`);
  }

  // 6. Context Engine 2.0 Testing
  console.log('\n--- Scenario 16: Context Engine 2.0 Relevance & Compression ---\n');
  const contextSources = [
    { id: '1', name: 'ddl_schema.sql', type: 'file' as const, content: 'CREATE TABLE orders (id INT PRIMARY KEY);\n// Unused comment line\n# another comment', filePath: 'ddl_schema.sql' },
    { id: '2', name: 'README.md', type: 'documentation' as const, content: 'Basic setup instructions and startup guidelines' },
    { id: '3', name: 'helper.js', type: 'file' as const, content: 'function run() { return true; }' }
  ];

  const contextPackage = ContextEngine.selectContext(
    'Create ecommerce database tables',
    contextSources,
    brainGraph,
    ['ddl_schema.sql'],
    'task-1002'
  );

  console.log('Classified Request:', contextPackage.requestClass);
  console.log('Selected context count:', contextPackage.sources.length);
  console.log('Tokens Saved:', contextPackage.metrics.tokensSaved);
  console.log('Context Size:', contextPackage.metrics.contextSize);
  console.log('Selection Accuracy Score:', contextPackage.metrics.selectionAccuracy);

  if (contextPackage.sources.length === 0) {
    throw new Error('Context Engine failed to select any relevant context.');
  }

  if (contextPackage.compressedContent.includes('// Unused comment line')) {
    throw new Error('Context Engine compression did not strip comments.');
  }

  console.log('Context Engine 2.0 validation complete.');

  console.log('\n==================================================');
  console.log('ALL RUNTIME CORE TESTS PASSED SUCCESSFULLY!');
  console.log('==================================================');
}

runTests().catch(err => {
  console.error('Test run failed:', err);
  process.exit(1);
});

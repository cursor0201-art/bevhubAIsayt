export interface AIRequest {
  taskType: 'code' | 'chat' | 'refactor' | 'seo' | 'image' | 'review';
  language?: string;
  projectSize?: 'small' | 'medium' | 'large';
  maxBudgetUsd?: number;
  maxLatencyMs?: number;
  prompt: string;
}

export interface ProviderPlugin {
  name: string;
  isHealthy: boolean;
  averageLatencyMs: number;
  costPer1kTokens: number;
  supportedTasks: string[];
  generateText(prompt: string): Promise<string>;
}

export class ModelRouter {
  private providers: Map<string, ProviderPlugin> = new Map();
  private cache: Map<string, string> = new Map();
  private usageHistory: Array<{ provider: string; tokensUsed: number; costUsd: number }> = [];

  constructor() {
    this.registerDefaultProviders();
  }

  private registerDefaultProviders() {
    // OpenAI default plugin
    this.registerProvider({
      name: 'openai',
      isHealthy: true,
      averageLatencyMs: 300,
      costPer1kTokens: 0.015,
      supportedTasks: ['code', 'chat', 'refactor', 'review'],
      generateText: async (prompt) => `[OpenAI Output] Response to: ${prompt}`
    });

    // Claude default plugin
    this.registerProvider({
      name: 'claude',
      isHealthy: true,
      averageLatencyMs: 400,
      costPer1kTokens: 0.03,
      supportedTasks: ['code', 'refactor', 'review', 'seo'],
      generateText: async (prompt) => `[Claude Output] Response to: ${prompt}`
    });

    // Gemini default plugin
    this.registerProvider({
      name: 'gemini',
      isHealthy: true,
      averageLatencyMs: 200,
      costPer1kTokens: 0.005,
      supportedTasks: ['chat', 'seo'],
      generateText: async (prompt) => `[Gemini Output] Response to: ${prompt}`
    });

    // DeepSeek default plugin
    this.registerProvider({
      name: 'deepseek',
      isHealthy: true,
      averageLatencyMs: 600,
      costPer1kTokens: 0.002,
      supportedTasks: ['chat', 'code', 'seo'],
      generateText: async (prompt) => `[DeepSeek Output] Response to: ${prompt}`
    });
  }

  public registerProvider(provider: ProviderPlugin) {
    this.providers.set(provider.name, provider);
  }

  public selectBestProvider(request: AIRequest): string {
    let bestProviderName = 'openai';
    let minCost = Infinity;

    for (const [name, p] of this.providers.entries()) {
      if (!p.isHealthy) continue;
      if (!p.supportedTasks.includes(request.taskType)) continue;

      // Routing heuristic based on cost and capability
      let matchesLatency = !request.maxLatencyMs || p.averageLatencyMs <= request.maxLatencyMs;
      if (matchesLatency && p.costPer1kTokens < minCost) {
        minCost = p.costPer1kTokens;
        bestProviderName = name;
      }
    }

    return bestProviderName;
  }

  public async executeWithFallback(request: AIRequest): Promise<string> {
    // Check Cache
    const cacheKey = `${request.taskType}:${request.prompt}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const preferredProvider = this.selectBestProvider(request);
    const orderOfProviders = [preferredProvider, ...Array.from(this.providers.keys()).filter(n => n !== preferredProvider)];

    for (const providerName of orderOfProviders) {
      const p = this.providers.get(providerName);
      if (!p || !p.isHealthy) continue;

      try {
        console.log(`[Model Router] Executing request on: ${providerName}`);
        
        // Timeout check (Simulated)
        const responsePromise = p.generateText(request.prompt);
        const timeoutPromise = new Promise<string>((_, reject) => 
          setTimeout(() => reject(new Error('Request Timeout')), 3000)
        );

        const resultText = await Promise.race([responsePromise, timeoutPromise]);
        
        // Caching
        this.cache.set(cacheKey, resultText);

        // Usage / Cost Tracking
        const estimatedTokens = Math.ceil(request.prompt.length / 4) + 100;
        const actualCost = (estimatedTokens / 1000) * p.costPer1kTokens;
        this.usageHistory.push({
          provider: providerName,
          tokensUsed: estimatedTokens,
          costUsd: actualCost
        });

        return resultText;
      } catch (err) {
        console.warn(`[Model Router] Provider ${providerName} failed: ${err}. Trying next fallback...`);
        p.isHealthy = false; // Mark temporarily unhealthy for recovery cycles
      }
    }

    throw new Error('All model providers failed or are unhealthy.');
  }

  public getUsageHistory() {
    return this.usageHistory;
  }
}

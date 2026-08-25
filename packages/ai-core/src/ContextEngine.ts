import { EngineeringGraph } from './EngineeringGraph';

export interface ContextSource {
  id: string;
  name: string;
  type: 'file' | 'architecture' | 'template' | 'memory' | 'documentation';
  content: string;
  filePath?: string;
}

export interface ScoredContext {
  source: ContextSource;
  relevanceScore: number;
}

export interface ContextPackage {
  requestClass: string;
  sources: ScoredContext[];
  compressedContent: string;
  metrics: {
    tokensSaved: number;
    contextSize: number;
    selectionAccuracy: number;
  };
}

export class ContextEngine {
  private static cache: Map<string, ContextPackage> = new Map();

  public static classifyRequest(prompt: string): string {
    const lowered = prompt.toLowerCase();
    if (lowered.includes('landing')) return 'landing_page';
    if (lowered.includes('crm') || lowered.includes('management')) return 'crm';
    if (lowered.includes('ecommerce') || lowered.includes('e-commerce') || lowered.includes('shop') || lowered.includes('store')) return 'ecommerce';
    if (lowered.includes('saas') || lowered.includes('ai')) return 'ai_saas';
    if (lowered.includes('bot') || lowered.includes('telegram')) return 'telegram_bot';
    return 'general_feature';
  }

  /**
   * Main entrypoint for Context Engine 2.0
   * Evaluates files, Git changes, and Graph proximity to select minimum necessary context.
   */
  public static selectContext(
    prompt: string,
    sources: ContextSource[],
    engGraph: EngineeringGraph,
    gitChanges: string[] = [],
    taskId = 'default-task'
  ): ContextPackage {
    const cacheKey = `${prompt}:${taskId}:${sources.length}:${gitChanges.join(',')}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const requestClass = this.classifyRequest(prompt);
    const scored: ScoredContext[] = [];

    // Calculate baseline and dynamic scores
    for (const src of sources) {
      let score = 0.2; // base score

      // 1. Proximity in the Engineering Graph
      if (src.filePath) {
        const graphNode = engGraph.getNodeByFilePath(src.filePath);
        if (graphNode) {
          // Connected nodes boost score
          score += 0.3;
          if (graphNode.status === 'outdated') {
            score += 0.2; // high relevance for outdated nodes
          }
        }
      }

      // 2. Git changes match boost
      if (src.filePath && gitChanges.some(change => src.filePath!.includes(change))) {
        score += 0.4;
      }

      // 3. Prompt keyword relevance match
      const promptWords = prompt.toLowerCase().split(/\s+/);
      const contentLower = src.content.toLowerCase();
      let matchCount = 0;
      for (const word of promptWords) {
        if (word.length > 3 && contentLower.includes(word)) {
          matchCount++;
        }
      }
      score += Math.min(0.3, matchCount * 0.05);

      // 4. Request class type match
      if (src.name.toLowerCase().includes(requestClass)) {
        score += 0.2;
      }

      scored.push({
        source: src,
        relevanceScore: Math.min(1.0, score)
      });
    }

    // Rank and filter (only keep >= 0.35 relevance)
    const ranked = scored
      .filter(item => item.relevanceScore >= 0.35)
      .sort((a, b) => b.relevanceScore - a.relevanceScore);

    // Remove duplicates
    const unique: ScoredContext[] = [];
    const seenNames = new Set<string>();
    for (const item of ranked) {
      if (!seenNames.has(item.source.name)) {
        seenNames.add(item.source.name);
        unique.push(item);
      }
    }

    // Compress content (strip comments, whitespace, truncate files over limit)
    let originalTokenEstimate = 0;
    let compressedTokenEstimate = 0;

    const compressedParts = unique.map(item => {
      const origLength = item.source.content.length;
      originalTokenEstimate += Math.ceil(origLength / 4);

      // Compress content by removing trailing whitespaces and header info
      const header = `[File: ${item.source.name} (Relevance: ${item.source.filePath ? 'Graph' : 'Text'} score: ${item.relevanceScore.toFixed(2)})]`;
      const cleanContent = item.source.content
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0 && !line.startsWith('//') && !line.startsWith('#'))
        .join('\n');

      const finalContent = cleanContent.length > 600
        ? cleanContent.substring(0, 600) + '\n... [truncated] ...'
        : cleanContent;

      compressedTokenEstimate += Math.ceil(finalContent.length / 4);
      return `${header}\n${finalContent}`;
    });

    const tokensSaved = Math.max(0, originalTokenEstimate - compressedTokenEstimate);
    const selectionAccuracy = unique.length > 0 
      ? unique.reduce((sum, item) => sum + item.relevanceScore, 0) / unique.length
      : 1.0;

    const resultPackage: ContextPackage = {
      requestClass,
      sources: unique,
      compressedContent: compressedParts.join('\n\n'),
      metrics: {
        tokensSaved,
        contextSize: compressedTokenEstimate,
        selectionAccuracy
      }
    };

    this.cache.set(cacheKey, resultPackage);
    return resultPackage;
  }

  public static scoreAndSelectContext(
    prompt: string,
    sources: ContextSource[]
  ): ContextPackage {
    return this.selectContext(prompt, sources, new EngineeringGraph());
  }

  public static clearCache(): void {
    this.cache.clear();
  }
}

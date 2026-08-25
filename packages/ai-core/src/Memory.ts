export interface MemoryEntry {
  key: string;
  value: any;
  timestamp: number;
}

export class Memory {
  private static instance: Memory;
  private entries: Map<string, MemoryEntry> = new Map();

  private constructor() {}

  public static getInstance(): Memory {
    if (!Memory.instance) {
      Memory.instance = new Memory();
    }
    return Memory.instance;
  }

  public set(key: string, value: any): void {
    this.entries.set(key, {
      key,
      value,
      timestamp: Date.now()
    });
    console.log(`[Memory] Stored item for key '${key}'`);
  }

  public get(key: string): any | null {
    const entry = this.entries.get(key);
    return entry ? entry.value : null;
  }

  public getRecent(limit: number = 10): MemoryEntry[] {
    return Array.from(this.entries.values())
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  public clear(): void {
    this.entries.clear();
  }
}

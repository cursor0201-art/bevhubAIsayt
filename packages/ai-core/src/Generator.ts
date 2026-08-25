export interface ProjectStructure {
  files: Map<string, string>;
  version: number;
}

export class ProjectGenerator {
  private history: ProjectStructure[] = [];
  private historyIndex: number = -1;

  constructor() {}

  public generateProject(prompt: string): ProjectStructure {
    const files = new Map<string, string>();
    
    // Auto-generate based on requirements
    files.set('README.md', `# Generated project for: ${prompt}\nCreated by BevHub AI Builder.`);
    files.set('src/pages/index.html', `<!DOCTYPE html><html><head><title>Home</title></head><body><h1>Welcome to ${prompt}</h1></body></html>`);
    files.set('src/database/schema.sql', `-- Auto-generated schema\nCREATE TABLE app_data (id UUID PRIMARY KEY);`);
    files.set('src/api/routes.json', JSON.stringify({ endpoints: [{ path: '/api/v1/status', method: 'GET' }] }, null, 2));

    const state: ProjectStructure = { files, version: 1 };
    this.pushState(state);
    return state;
  }

  private pushState(state: ProjectStructure) {
    // Trim forward history if we were in the middle of undos
    if (this.historyIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyIndex + 1);
    }
    this.history.push(state);
    this.historyIndex = this.history.length - 1;
    console.log(`[AI Builder] Saved state version ${state.version}. Index: ${this.historyIndex}`);
  }

  public editFile(path: string, newContent: string): ProjectStructure {
    const current = this.history[this.historyIndex];
    const newFiles = new Map(current.files);
    newFiles.set(path, newContent);

    const nextState: ProjectStructure = {
      files: newFiles,
      version: current.version + 1
    };
    this.pushState(nextState);
    return nextState;
  }

  public undo(): ProjectStructure | null {
    if (this.historyIndex > 0) {
      this.historyIndex--;
      console.log(`[AI Builder] Undo successful. Index: ${this.historyIndex}`);
      return this.history[this.historyIndex];
    }
    return null;
  }

  public redo(): ProjectStructure | null {
    if (this.historyIndex < this.history.length - 1) {
      this.historyIndex++;
      console.log(`[AI Builder] Redo successful. Index: ${this.historyIndex}`);
      return this.history[this.historyIndex];
    }
    return null;
  }

  public getCurrentState(): ProjectStructure {
    return this.history[this.historyIndex];
  }
}

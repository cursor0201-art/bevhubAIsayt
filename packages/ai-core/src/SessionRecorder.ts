export interface SessionStep {
  name: string;
  type: 'request' | 'planning' | 'context_fetch' | 'llm_call' | 'validation' | 'deploy' | 'metrics';
  status: 'success' | 'failed';
  payload: Record<string, any>;
  durationMs: number;
  timestamp: number;
}

export interface SessionRecord {
  sessionId: string;
  taskPrompt: string;
  steps: SessionStep[];
  startedAt: number;
  completedAt?: number;
}

export class SessionRecorder {
  private currentSession: SessionRecord | null = null;
  private history: Map<string, SessionRecord> = new Map();

  constructor() {}

  public startSession(sessionId: string, taskPrompt: string): SessionRecord {
    this.currentSession = {
      sessionId,
      taskPrompt,
      steps: [],
      startedAt: Date.now()
    };
    this.history.set(sessionId, this.currentSession);
    console.log(`[Session Recorder] Started recording session: ${sessionId}`);
    return this.currentSession;
  }

  public recordStep(
    name: string,
    type: SessionStep['type'],
    status: SessionStep['status'],
    payload: Record<string, any>,
    durationMs: number
  ): SessionStep {
    if (!this.currentSession) {
      throw new Error('No active recording session.');
    }

    const step: SessionStep = {
      name,
      type,
      status,
      payload,
      durationMs,
      timestamp: Date.now()
    };

    this.currentSession.steps.push(step);
    console.log(`[Session Recorder] Recorded step '${name}' [${type}] with status: ${status}`);
    return step;
  }

  public endSession(status: 'success' | 'failed'): SessionRecord {
    if (!this.currentSession) {
      throw new Error('No active recording session.');
    }

    this.currentSession.completedAt = Date.now();
    console.log(`[Session Recorder] Ended session: ${this.currentSession.sessionId} with status: ${status}`);
    
    const finished = this.currentSession;
    this.currentSession = null;
    return finished;
  }

  public getSession(sessionId: string): SessionRecord | undefined {
    return this.history.get(sessionId);
  }

  public rewindToStep(sessionId: string, stepName: string): SessionStep[] {
    const session = this.history.get(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    const stepIndex = session.steps.findIndex(s => s.name === stepName);
    if (stepIndex === -1) {
      throw new Error(`Step not found in session: ${stepName}`);
    }

    console.log(`[Session Recorder] Rewinding session ${sessionId} to step: ${stepName}`);
    return session.steps.slice(0, stepIndex + 1);
  }
}

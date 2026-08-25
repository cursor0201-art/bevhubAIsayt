import { APIClient } from './apiClient';

export interface AITaskData {
  id: string;
  workspace: string | null;
  project: string | null;
  prompt: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  logs: string;
  tokens_used: number;
  duration_ms: number;
  created_at: string;
}

export class AITaskService {
  public static async createTask(prompt: string, workspaceId?: string, projectId?: string): Promise<AITaskData> {
    return APIClient.post<AITaskData>('/api/ai/tasks/', {
      prompt,
      workspace_id: workspaceId,
      project_id: projectId
    });
  }

  public static async getTask(taskId: string): Promise<AITaskData> {
    return APIClient.get<AITaskData>(`/api/ai/tasks/${taskId}/`);
  }

  public static async getTaskProgress(taskId: string): Promise<AITaskProgressData> {
    return APIClient.get<AITaskProgressData>(`/api/ai/tasks/${taskId}/progress/`);
  }
}

export interface GenerationStepData {
  id: string;
  step_name: string;
  status: 'PENDING' | 'RUNNING' | 'FAILED' | 'SUCCESS';
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  tokens_used: number;
  model_name: string;
  cost: number;
  error_message: string;
}

export interface AITaskProgressData {
  task_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress_percent: number;
  current_stage: string;
  active_model: string;
  total_cost: number;
  estimated_remaining_seconds: number;
  last_log: string;
  steps: GenerationStepData[];
}

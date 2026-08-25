import { APIClient } from './apiClient';

export interface GenerationResponse {
  task_id: string;
  status: 'queued' | 'processing' | 'success' | 'failed';
  result?: {
    design_system: Record<string, string>;
    copy: string;
    seo: Record<string, any>;
  };
}

export class AIService {
  public static async triggerGeneration(projectId: string, prompt: string): Promise<GenerationResponse> {
    return APIClient.post<GenerationResponse>(`/api/projects/${projectId}/generate/`, { prompt });
  }

  public static async checkGenerationStatus(projectId: string, taskId: string): Promise<GenerationResponse> {
    return APIClient.get<GenerationResponse>(`/api/projects/${projectId}/generate/status/`, {
      params: { task_id: taskId },
    });
  }
}

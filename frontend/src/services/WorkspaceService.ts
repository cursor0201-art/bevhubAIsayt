import { APIClient } from './apiClient';

export interface WorkspaceData {
  id: string;
  name: string;
  settings: Record<string, any>;
  created_at: string;
}

export class WorkspaceService {
  public static async getWorkspaces(): Promise<WorkspaceData[]> {
    return APIClient.get<WorkspaceData[]>('/api/workspaces/');
  }

  public static async createWorkspace(name: string): Promise<WorkspaceData> {
    return APIClient.post<WorkspaceData>('/api/workspaces/', { name });
  }
}

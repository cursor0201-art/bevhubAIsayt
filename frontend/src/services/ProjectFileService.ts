import { APIClient } from './apiClient';
import { ProjectData } from './ProjectService';

export interface ProjectFileData {
  id: string;
  path: string;
  content: string;
  created_at: string;
}

export class ProjectFileService {
  public static async updateFile(fileId: string, content: string): Promise<ProjectFileData> {
    return APIClient.patch<ProjectFileData>(`/api/files/${fileId}/`, { content });
  }

  public static async createFile(projectId: string, path: string, content: string): Promise<ProjectFileData> {
    return APIClient.post<ProjectFileData>('/api/files/', {
      project_id: projectId,
      path,
      content
    });
  }
}

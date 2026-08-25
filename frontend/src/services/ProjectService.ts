import { APIClient } from './apiClient';
import { ProjectFileData } from './ProjectFileService';

export interface PageData {
  id: string;
  slug: string;
  title: string;
  layout_ast: Record<string, any>;
  raw_content: string;
  created_at: string;
}

export interface DeploymentData {
  id: string;
  status: 'queued' | 'processing' | 'success' | 'failed';
  commit_hash: string;
  deploy_url: string;
  created_at: string;
}

export interface ProjectData {
  id: string;
  project_name: string;
  subdomain: string;
  custom_domain: string | null;
  design_system: Record<string, any>;
  status: string;
  version: number;
  pages: PageData[];
  deployments: DeploymentData[];
  files: ProjectFileData[];
  created_at: string;
}


export class ProjectService {
  public static async getProjects(workspaceId?: string): Promise<ProjectData[]> {
    const url = workspaceId ? `/api/projects/?workspace_id=${workspaceId}` : '/api/projects/';
    return APIClient.get<ProjectData[]>(url);
  }

  public static async getProject(projectId: string): Promise<ProjectData> {
    return APIClient.get<ProjectData>(`/api/projects/${projectId}/`);
  }

  // --- Real-Time Generation AI Task Endpoints ---
  public static async createAITask(prompt: string, workspaceId: string): Promise<{ id: string; status: string }> {
    return APIClient.post('/api/ai-tasks/', { prompt, workspace_id: workspaceId });
  }

  public static async getAITask(taskId: string): Promise<{ id: string; project: string | null; status: string }> {
    return APIClient.get(`/api/ai-tasks/${taskId}/`);
  }

  public static async getAITasks(): Promise<any[]> {
    return APIClient.get('/api/ai-tasks/');
  }

  public static async getAITaskProgress(taskId: string): Promise<any> {
    return APIClient.get(`/api/ai-tasks/${taskId}/progress/`);
  }
  // ----------------------------------------------

  public static async createProject(data: { project_name: string; subdomain: string; workspace_id?: string }): Promise<ProjectData> {
    return APIClient.post<ProjectData>('/api/projects/', data);
  }

  public static async updateProject(projectId: string, data: Partial<ProjectData>): Promise<ProjectData> {
    return APIClient.put<ProjectData>(`/api/projects/${projectId}/`, data);
  }

  public static async deleteProject(projectId: string): Promise<void> {
    return APIClient.delete<void>(`/api/projects/${projectId}/`);
  }

  public static async generateProject(prompt: string, workspaceId?: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>('/api/projects/generate/', { prompt, workspace_id: workspaceId });
  }

  public static async updatePage(projectId: string, slug: string, rawContent: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/update-page/`, { slug, raw_content: rawContent });
  }

  public static async deployProject(projectId: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/deploy/`, {});
  }

  public static async archiveProject(projectId: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/archive/`, {});
  }

  public static async restoreProject(projectId: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/restore/`, {});
  }

  public static async duplicateProject(projectId: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/duplicate/`, {});
  }

  public static async aiEditProject(projectId: string, prompt: string, filepath?: string): Promise<ProjectData> {
    return APIClient.post<ProjectData>(`/api/projects/${projectId}/ai-edit/`, { prompt, filepath });
  }

  public static async getProjectReviews(projectId: string): Promise<ProjectReviewData[]> {
    return APIClient.get<ProjectReviewData[]>(`/api/projects/${projectId}/reviews/`);
  }

  public static async createProjectReview(projectId: string): Promise<ProjectReviewData> {
    return APIClient.post<ProjectReviewData>(`/api/projects/${projectId}/review/`, {});
  }

  public static async fixProject(projectId: string): Promise<ProjectFixData> {
    return APIClient.post<ProjectFixData>(`/api/projects/${projectId}/fix/`, {});
  }

  public static async getProjectFixes(projectId: string): Promise<ProjectFixRunRecord[]> {
    return APIClient.get<ProjectFixRunRecord[]>(`/api/projects/${projectId}/fixes/`);
  }

  // --- Real-Time Modules API Endpoints ---
  public static async getTemplates(): Promise<any[]> {
    return APIClient.get('/api/templates/');
  }

  public static async getHistory(search?: string, status?: string): Promise<any[]> {
    let url = '/api/analytics/history/';
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status && status !== 'all') params.append('status', status);
    if (params.toString()) url += `?${params.toString()}`;
    return APIClient.get(url);
  }

  public static async getDeployments(): Promise<any[]> {
    return APIClient.get('/api/deployments/');
  }

  public static async redeploy(deploymentId: string): Promise<any> {
    return APIClient.post(`/api/deployments/${deploymentId}/redeploy/`, {});
  }

  public static async getIntegrations(): Promise<any[]> {
    return APIClient.get('/api/integrations/');
  }

  public static async connectIntegration(provider: string, config: any = {}): Promise<any> {
    return APIClient.post(`/api/integrations/${provider}/connect/`, { config });
  }

  public static async disconnectIntegration(provider: string): Promise<any> {
    return APIClient.post(`/api/integrations/${provider}/disconnect/`, {});
  }

  public static async getProfile(): Promise<any> {
    return APIClient.get('/api/auth/me/');
  }

  public static async updateProfile(data: { username?: string; email?: string; theme?: string; language?: string }): Promise<any> {
    return APIClient.patch('/api/auth/me/', data);
  }

  public static async changePassword(oldPassword: string, newPassword: string): Promise<any> {
    return APIClient.post('/api/auth/change-password/', { old_password: oldPassword, new_password: newPassword });
  }

  public static async deleteAccount(password: string): Promise<any> {
    return APIClient.post('/api/auth/delete-account/', { password });
  }
}

export interface ProjectReviewData {
  id: string;
  project: string;
  overall_score: number;
  architecture_score: number;
  performance_score: number;
  security_score: number;
  seo_score: number;
  accessibility_score: number;
  ux_score: number;
  typescript_score: number;
  react_score: number;
  deployment_score: number;
  issues: Array<{ severity: 'critical' | 'high' | 'medium' | 'low'; title: string; description: string }>;
  recommendations: string[];
  created_at: string;
}

export interface ProjectFixData {
  before_score: number;
  after_score: number;
  fixed: number;
  remaining: number;
  rollback_available: boolean;
  snapshot_id: string;
  fix_run_id?: string;
}

export interface ProjectFixRunRecord {
  id: string;
  project: string;
  before_score: number;
  after_score: number;
  fixed_count: number;
  remaining_count: number;
  rollback_applied: boolean;
  snapshot: string | null;
  logs: Array<{
    issue_id: string;
    severity: string;
    reason: string;
    root_cause: string;
    affected_files: string[];
    fix_strategy: string;
    success: boolean;
    lines_modified: string;
    explanation: string;
    model: string;
    duration_ms: number;
  }>;
  created_at: string;
}





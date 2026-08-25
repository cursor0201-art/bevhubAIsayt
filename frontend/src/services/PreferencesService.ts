import { APIClient } from './apiClient';

export interface PreferencesData {
  writing_style: string;
  favorite_colors: string[];
  preferred_language: string;
}

export class PreferencesService {
  public static async getPreferences(): Promise<PreferencesData> {
    return APIClient.get<PreferencesData>('/api/ai/preferences/');
  }

  public static async updatePreferences(data: Partial<PreferencesData>): Promise<PreferencesData> {
    return APIClient.post<PreferencesData>('/api/ai/preferences/', data);
  }
}

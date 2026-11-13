const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  avatar_url?: string;
}

export interface ProviderItem {
  id: string;
  provider: string;
  masked_key: string;
  default_model?: string;
  status: string;
  is_default: boolean;
  last_verified_at?: string;
  created_at: string;
}

export interface QuestionAnalysis {
  question: string;
  suggested_answer: string;
  answer_text: string;
  original_label?: string | null;
  source_position?: number | null;
  explanation: string;
  option_analysis: Record<string, string>;
  confidence: {
    level: string;
    reason: string;
  };
  subject: string;
  subject_confidence?: number;
  curriculum_confidence?: number;
  evidence?: string | null;
  is_ambiguous?: boolean;
  ambiguity_details?: string[] | null;
  needs_review: boolean;
  structured_options?: any[];
  input_tokens: number;
  output_tokens: number;
  estimated_cost: number;
}

export interface QuestionRecord {
  id: string;
  question_text: string;
  options: Record<string, string>;
  suggested_answer: string;
  answer_text: string;
  explanation: string;
  option_analysis: Record<string, string>;
  confidence_level: string;
  confidence_reason: string;
  subject: string;
  provider: string;
  model: string;
  user_feedback?: string;
  created_at: string;
}

class ApiService {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("exampilot_token") || sessionStorage.getItem("exampilot_token");
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("exampilot_token", token);
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== "undefined") {
      this.token = localStorage.getItem("exampilot_token");
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("exampilot_token");
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let errDetail = "Request failed";
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
      } catch {
        errDetail = await res.text();
      }
      throw new Error(errDetail || `HTTP error ${res.status}`);
    }

    return res.json();
  }

  // Auth
  async register(email: string, password: string, displayName?: string) {
    const data = await this.request<{ access_token: string; user: UserProfile }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string; user: UserProfile }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>("/auth/profile");
  }

  // Providers
  async getProviders(): Promise<ProviderItem[]> {
    return this.request<ProviderItem[]>("/providers");
  }

  async saveProvider(provider: string, apiKey: string, defaultModel?: string, isDefault: boolean = false): Promise<ProviderItem> {
    return this.request<ProviderItem>("/providers", {
      method: "POST",
      body: JSON.stringify({
        provider,
        api_key: apiKey,
        default_model: defaultModel,
        is_default: isDefault,
      }),
    });
  }

  async testProvider(provider: string, apiKey?: string) {
    return this.request<{ success: boolean; status: string; message: string }>("/providers/test", {
      method: "POST",
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  }

  async getModels(provider?: string) {
    const query = provider ? `?provider=${encodeURIComponent(provider)}` : "";
    return this.request<any[]>(`/providers/models${query}`);
  }

  async setDefaultProvider(provider: string, defaultModel?: string) {
    return this.request<{ message: string }>("/providers/default", {
      method: "POST",
      body: JSON.stringify({ provider, default_model: defaultModel }),
    });
  }

  async deleteProvider(providerId: string) {
    return this.request<{ message: string }>(`/providers/${providerId}`, {
      method: "DELETE",
    });
  }

  // OCR
  async scanImageFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return this.request<any>("/ocr/image", {
      method: "POST",
      body: formData,
    });
  }

  async scanImageBase64(base64: string) {
    const formData = new FormData();
    formData.append("image_base64", base64);
    return this.request<any>("/ocr/image", {
      method: "POST",
      body: formData,
    });
  }

  async scanPdfFile(file: File, maxPages: number = 10) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("max_pages", String(maxPages));
    return this.request<any>("/ocr/pdf", {
      method: "POST",
      body: formData,
    });
  }

  // Questions
  async analyseQuestion(data: {
    question_text: string;
    options: Record<string, string>;
    structured_options?: any[];
    subject?: string;
    provider?: string;
    model?: string;
    context_material?: string;
  }): Promise<QuestionAnalysis> {
    return this.request<QuestionAnalysis>("/questions/analyse", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getQuestions(search?: string, subject?: string): Promise<QuestionRecord[]> {
    let url = "/questions?";
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (subject && subject !== "All") url += `subject=${encodeURIComponent(subject)}&`;
    return this.request<QuestionRecord[]>(url);
  }

  async submitFeedback(questionId: string, feedback: string) {
    return this.request<any>(`/questions/${questionId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ feedback }),
    });
  }

  async deleteQuestion(questionId: string) {
    return this.request<any>(`/questions/${questionId}`, {
      method: "DELETE",
    });
  }

  // Assistant
  async getConversations() {
    return this.request<any[]>("/assistant/conversations");
  }

  async createConversation(title?: string, provider?: string, model?: string) {
    return this.request<any>("/assistant/conversations", {
      method: "POST",
      body: JSON.stringify({ title, provider, model }),
    });
  }

  async getConversation(id: string) {
    return this.request<any>(`/assistant/conversations/${id}`);
  }

  async sendChatMessage(conversationId: string, content: string, provider?: string, model?: string) {
    return this.request<any>("/assistant/chat", {
      method: "POST",
      body: JSON.stringify({
        conversation_id: conversationId,
        content,
        provider,
        model,
      }),
    });
  }

  // Practice
  async listPracticeSessions() {
    return this.request<any[]>("/practice");
  }

  async createPracticeTest(title: string, subject?: string, count: number = 5, timeLimit: number = 10) {
    return this.request<any>("/practice", {
      method: "POST",
      body: JSON.stringify({
        title,
        subject,
        question_count: count,
        time_limit_minutes: timeLimit,
      }),
    });
  }

  async submitPracticeTest(sessionId: string, answers: { question_id: string; selected_answer: string }[]) {
    return this.request<any>("/practice/submit", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        answers,
      }),
    });
  }

  // Documents
  async listDocuments() {
    return this.request<any[]>("/documents");
  }

  async uploadDocument(file: File, subjectName?: string) {
    const formData = new FormData();
    formData.append("file", file);
    if (subjectName) formData.append("subject_name", subjectName);
    return this.request<any>("/documents/upload", {
      method: "POST",
      body: formData,
    });
  }

  async searchDocuments(query: string) {
    return this.request<any>("/documents/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  }

  async deleteDocument(id: string) {
    return this.request<any>(`/documents/${id}`, {
      method: "DELETE",
    });
  }

  // Analytics
  async getAnalyticsOverview() {
    return this.request<any>("/analytics/overview");
  }

  async getSubjectAnalytics() {
    return this.request<any>("/analytics/subjects");
  }

  async getUsageAnalytics() {
    return this.request<any>("/analytics/usage");
  }

  // Settings
  async getSettings() {
    return this.request<any>("/settings");
  }

  async saveSetting(key: string, value: string) {
    return this.request<any>("/settings", {
      method: "PUT",
      body: JSON.stringify({ setting_key: key, setting_value: value }),
    });
  }

  async exportData() {
    return this.request<any>("/settings/export");
  }

  async deleteAccount(confirmEmail: string) {
    return this.request<any>("/settings/account", {
      method: "DELETE",
      body: JSON.stringify({ confirm_email: confirmEmail }),
    });
  }
}

export const api = new ApiService();


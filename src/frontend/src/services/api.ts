// AROHA API service – centralised HTTP client for backend communication
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiOptions extends RequestInit {
  noAuth?: boolean;
}

class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { noAuth, ...fetchOptions } = options;
  const url = `${API_BASE}${path}`;

  const headers: Record<string, string> = {
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(fetchOptions.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  const res = await fetch(url, {
    ...fetchOptions,
    headers,
    credentials: "include", // send cookies (aroha_session)
  });

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {
      // response wasn't JSON
    }
    throw new ApiError(res.status, detail);
  }

  // Handle 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
}

export const auth = {
  register(data: { name: string; email: string; password: string }) {
    return request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
      noAuth: true,
    });
  },

  login(data: { email: string; password: string }) {
    return request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
      noAuth: true,
    });
  },

  logout() {
    return request<void>("/auth/logout", { method: "POST" });
  },

  me() {
    return request<User>("/auth/me");
  },

  forgotPassword(email: string) {
    return request<{ detail: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
      noAuth: true,
    });
  },
};

// ─── Users ───────────────────────────────────────────────────────────────────

export interface UserSettings {
  connected_accounts: InstagramAccount[];
  consents: ConsentRecord[];
}

export interface ConsentRecord {
  consent_type: string;
  consent_status: string;
  recorded_at: string;
  withdrawn_at: string | null;
}

export const users = {
  getProfile() {
    return request<User>("/users/profile");
  },

  updateProfile(data: { name: string }) {
    return request<User>("/users/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  getSettings() {
    return request<UserSettings>("/users/settings");
  },

  deleteAccount() {
    return request<void>("/users/account", { method: "DELETE" });
  },
};

// ─── Consent ─────────────────────────────────────────────────────────────────

export const consent = {
  getAll() {
    return request<Record<string, ConsentRecord>>("/users/consent");
  },

  update(consentType: "media_retention" | "model_training", granted: boolean) {
    return request<ConsentRecord>("/users/consent", {
      method: "PUT",
      body: JSON.stringify({ consent_type: consentType, granted }),
    });
  },
};

// ─── Instagram ───────────────────────────────────────────────────────────────

export interface InstagramAccount {
  platform: string;
  platform_user_id: string;
  username: string;
  connection_status: string;
  connected_at: string;
}

export interface GrowthPoint {
  date: string;
  followers: number;
}

export interface AnalyticsData {
  followers_count?: number;
  media_count?: number;
  [key: string]: number | undefined;
}

export const instagram = {
  getConnectUrl() {
    return request<{ url: string }>("/instagram/connect");
  },

  getAccount() {
    return request<InstagramAccount>("/instagram/account");
  },

  disconnect() {
    return request<{ detail: string }>("/instagram/disconnect", {
      method: "POST",
    });
  },

  sync() {
    return request<{ detail: string }>("/instagram/sync", {
      method: "POST",
    });
  },

  getGrowth() {
    return request<{ data: GrowthPoint[] }>("/instagram/growth");
  },

  getAnalytics() {
    return request<AnalyticsData>("/instagram/analytics");
  },

  getMedia() {
    return request<{ data: unknown[] }>("/instagram/media");
  },
};

// ─── Link Analyzer ───────────────────────────────────────────────────────────

export interface LinkReport {
  id: number;
  detected_url: string;
  response_status: number | null;
  validation_result: string;
  issue_description: string | null;
  checked_at: string;
}

export const links = {
  analyze(data: { text?: string; urls?: string[] }) {
    return request<LinkReport[]>("/links/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getReports() {
    return request<LinkReport[]>("/links/reports");
  },

  getReport(reportId: number) {
    return request<LinkReport>(`/links/reports/${reportId}`);
  },
};

// ─── Audio Detector ──────────────────────────────────────────────────────────

export interface AudioReport {
  id: number;
  detected_status: string;
  similarity_score: number | null;
  analysis_date: string;
  audio_reference_id: number | null;
}

export const audio = {
  uploadReference(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ reference_id: number }>("/audio/upload-reference", {
      method: "POST",
      body: formData,
    });
  },

  analyze(file: File, referenceId?: number) {
    const formData = new FormData();
    formData.append("file", file);
    if (referenceId) {
      formData.append("reference_id", String(referenceId));
    }
    return request<AudioReport>("/audio/analyze", {
      method: "POST",
      body: formData,
    });
  },

  getHistory() {
    return request<AudioReport[]>("/audio/history");
  },

  getReport(reportId: number) {
    return request<AudioReport>(`/audio/report/${reportId}`);
  },
};

// ─── Lip-Sync ────────────────────────────────────────────────────────────────

export interface LipSyncReport {
  id: number;
  video_reference: string;
  synchronization_status: string;
  estimated_offset_ms: number | null;
  confidence_score: number | null;
  analysis_report: Record<string, unknown> | null;
  created_at: string;
}

export const lipsync = {
  upload(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ job_id: number }>("/lipsync/upload", {
      method: "POST",
      body: formData,
    });
  },

  getStatus(jobId: number) {
    return request<{ status: string; progress: number }>(`/lipsync/status/${jobId}`);
  },

  getReport(reportId: number) {
    return request<LipSyncReport>(`/lipsync/report/${reportId}`);
  },
};

// ─── News ────────────────────────────────────────────────────────────────────

export interface NewsArticle {
  id: number;
  title: string;
  description: string | null;
  source: string;
  article_url: string;
  image_url: string | null;
  category: string;
  published_at: string | null;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export const news = {
  getArticles(params?: { category?: string; q?: string; skip?: number; limit?: number }) {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.q) searchParams.set("q", params.q);
    if (params?.skip) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    const qs = searchParams.toString();
    return request<NewsArticle[]>(`/news${qs ? `?${qs}` : ""}`, { noAuth: true });
  },

  getCategories() {
    return request<CategoryCount[]>("/news/categories", { noAuth: true });
  },

  getTrending() {
    return request<NewsArticle[]>("/news/trending", { noAuth: true });
  },

  getArticle(id: number) {
    return request<NewsArticle>(`/news/${id}`, { noAuth: true });
  },

  refresh() {
    return request<{ detail: string }>("/news/refresh", { method: "POST" });
  },
};

// ─── Notifications & Feature Catalogs ────────────────────────────────────────

export interface MediaItem {
  id: number;
  platform_media_id: string | null;
  media_type: string;
  media_reference: string | null;
  permalink: string | null;
  thumbnail_url: string | null;
  caption: string | null;
  created_at: string;
}

export interface IssueNotification {
  id: number;
  user_id: number;
  media_id: number | null;
  issue_category: "broken_link" | "audio_loss" | "lipsync_mismatch";
  issue_type: string;
  severity: "critical" | "warning" | "info";
  title: string;
  description: string;
  recommendation: string | null;
  detected_url: string | null;
  http_status: number | null;
  audio_status: string | null;
  previous_audio_ref: string | null;
  current_audio_status: string | null;
  similarity_score: number | null;
  sync_offset_ms: number | null;
  confidence_score: number | null;
  problem_timestamps: string | null;
  is_read: boolean;
  is_resolved: boolean;
  is_dismissed: boolean;
  analysis_timestamp: string;
  last_checked_at: string;
  resolved_at: string | null;
  media?: MediaItem | null;
}

export interface NotificationSummary {
  total_issues: number;
  broken_link_issues: number;
  audio_issues: number;
  lipsync_issues: number;
  unresolved_issues: number;
  resolved_issues: number;
  unread_count: number;
}

export const notifications = {
  getNotifications(params?: { category?: string; status?: string; media_id?: number; limit?: number; skip?: number }) {
    const sp = new URLSearchParams();
    if (params?.category) sp.set("category", params.category);
    if (params?.status) sp.set("status", params.status);
    if (params?.media_id !== undefined) sp.set("media_id", String(params.media_id));
    if (params?.limit !== undefined) sp.set("limit", String(params.limit));
    if (params?.skip !== undefined) sp.set("skip", String(params.skip));
    const qs = sp.toString();
    return request<IssueNotification[]>(`/notifications${qs ? `?${qs}` : ""}`);
  },

  getSummary() {
    return request<NotificationSummary>("/notifications/summary");
  },

  getCatalog(category: "broken_link" | "audio_loss" | "lipsync_mismatch", status: string = "all") {
    return request<IssueNotification[]>(`/notifications/catalog/${category}?status=${status}`);
  },

  getDetail(issueId: number) {
    return request<IssueNotification>(`/notifications/${issueId}`);
  },

  markRead(issueId: number) {
    return request<IssueNotification>(`/notifications/${issueId}/read`, { method: "PUT" });
  },

  markResolved(issueId: number) {
    return request<IssueNotification>(`/notifications/${issueId}/resolve`, { method: "PUT" });
  },

  markUnresolved(issueId: number) {
    return request<IssueNotification>(`/notifications/${issueId}/unresolve`, { method: "PUT" });
  },

  dismiss(issueId: number) {
    return request<{ dismissed: boolean; issue_id: number }>(`/notifications/${issueId}`, { method: "DELETE" });
  },

  triggerScan() {
    return request<{
      status: string;
      audited_media_count: number;
      new_issues_detected: number;
      existing_issues_updated: number;
    }>("/notifications/scan", { method: "POST" });
  },
};

export { ApiError };


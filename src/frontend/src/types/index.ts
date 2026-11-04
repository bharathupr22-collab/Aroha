// Shared TypeScript types for AROHA frontend

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

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

export interface LinkReport {
  id: number;
  detected_url: string;
  response_status: number | null;
  validation_result: string;
  issue_description: string | null;
  checked_at: string;
}

export interface AudioReport {
  id: number;
  detected_status: string;
  similarity_score: number | null;
  analysis_date: string;
  audio_reference_id: number | null;
}

export interface LipSyncReport {
  id: number;
  video_reference: string;
  synchronization_status: string;
  estimated_offset_ms: number | null;
  confidence_score: number | null;
  analysis_report: Record<string, unknown> | null;
  created_at: string;
}

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

export interface ConsentRecord {
  consent_type: string;
  consent_status: string;
  recorded_at: string;
  withdrawn_at: string | null;
}

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

export type DateRange = "7d" | "30d" | "90d" | "custom";

export type ValidationResult = "working" | "broken" | "redirected" | "error" | "unsafe" | "unreachable" | "invalid" | "redirect_loop";

export type AudioStatus = "intact" | "changed" | "replaced" | "missing" | "partially_silent";

export type SyncStatus =
  | "synchronized"
  | "minor_mismatch"
  | "significant_mismatch"
  | "audio_ahead"
  | "video_ahead"
  | "insufficient_data";

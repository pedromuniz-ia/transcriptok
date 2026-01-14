export type Platform = "tiktok" | "youtube" | "instagram";

export type JobStatus = "pending" | "processing" | "completed" | "failed";

export type ExportFormat = "txt" | "json" | "srt" | "vtt";

export type HookStyle = "curiosity" | "shock" | "question" | "story";

export type RewriteGoal = "more_viral" | "shorter" | "clearer";

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface Transcript {
  id: string;
  video_id: string;
  full_text: string;
  segments?: TranscriptSegment[];
  language?: string;
  confidence?: number;
  created_at: string;
}

export interface Video {
  id: string;
  platform: Platform;
  original_url: string;
  video_id?: string;
  title?: string;
  author?: string;
  duration?: number;
  thumbnail_url?: string;
  created_at: string;
}

export interface Job {
  id: string;
  type: "download" | "transcription" | "ai_tool";
  status: JobStatus;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  output_data?: Record<string, unknown>;
  error_message?: string;
}

export interface TranscriptHistoryItem {
  id: string;
  video: Video;
  transcript: Transcript;
  status: JobStatus;
}

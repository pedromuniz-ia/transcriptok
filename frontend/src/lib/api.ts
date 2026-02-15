const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface VideoDownloadRequest {
  url: string;
  quality?: "best" | "720p" | "480p";
  remove_watermark?: boolean;
}

export interface JobResponse {
  id: string;
  type: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
  completed_at?: string;
  output_data?: Record<string, unknown>;
  error_message?: string;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface TranscriptResponse {
  id: string;
  video_id: string;
  full_text: string;
  segments?: TranscriptSegment[];
  language?: string;
  confidence?: number;
  created_at: string;
}

export interface TranscriptListItem {
  id: string;
  video_id: string;
  video_title?: string;
  video_author?: string;
  platform?: string;
  duration?: number;
  language?: string;
  confidence?: number;
  job_status?: string;
  created_at: string;
}

export interface TranscriptListResponse {
  items: TranscriptListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface TranscriptListParams {
  limit?: number;
  offset?: number;
  status?: string;
  platform?: string;
  search?: string;
}

export interface HookGeneratorInput {
  transcript: string;
  style?: "curiosity" | "shock" | "question" | "story";
  count?: number;
}

export interface ScriptRewriterInput {
  original_script: string;
  goal?: "more_viral" | "shorter" | "clearer";
  tone?: string;
}

export interface ContentAnalyzerOutput {
  virality_score: number;
  strengths: string[];
  improvements: string[];
  suggested_hooks: string[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
  }

  private buildUrl(endpoint: string): string {
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    return `${this.baseUrl}${path}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = this.buildUrl(endpoint);
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Erro da API: ${response.status}`);
    }

    return response.json();
  }

  // Video endpoints
  async downloadVideo(data: VideoDownloadRequest): Promise<{ job_id: string }> {
    return this.request("/api/v1/videos/download", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getVideoJob(jobId: string): Promise<JobResponse> {
    return this.request(`/api/v1/videos/job/${jobId}`);
  }

  // Transcript endpoints
  async listTranscripts(
    params: TranscriptListParams = {}
  ): Promise<TranscriptListResponse> {
    const searchParams = new URLSearchParams();
    if (params.limit) searchParams.set("limit", String(params.limit));
    if (params.offset) searchParams.set("offset", String(params.offset));
    if (params.status) searchParams.set("status", params.status);
    if (params.platform) searchParams.set("platform", params.platform);
    if (params.search) searchParams.set("search", params.search);
    const qs = searchParams.toString();
    return this.request(`/api/v1/transcripts/${qs ? `?${qs}` : ""}`);
  }

  async createTranscript(data: {
    video_url?: string;
    job_id?: string;
  }): Promise<{ job_id: string }> {
    return this.request("/api/v1/transcripts/create", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getTranscriptJob(jobId: string): Promise<JobResponse> {
    return this.request(`/api/v1/transcripts/job/${jobId}`);
  }

  async getTranscript(transcriptId: string): Promise<TranscriptResponse> {
    return this.request(`/api/v1/transcripts/${transcriptId}`);
  }

  async exportTranscript(
    transcriptId: string,
    format: "txt" | "json" | "srt" | "vtt"
  ): Promise<Blob> {
    const response = await fetch(
      this.buildUrl(`/api/v1/transcripts/${transcriptId}/export`),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ format }),
      }
    );

    if (!response.ok) {
      throw new Error("Falha ao exportar");
    }

    return response.blob();
  }

  // AI Tools endpoints
  async generateHooks(
    input: HookGeneratorInput
  ): Promise<{ hooks: string[] }> {
    const response = await this.request<{ output: { hooks: string[] } }>(
      "/api/v1/ai/hooks",
      {
        method: "POST",
        body: JSON.stringify(input),
      }
    );
    return response.output;
  }

  async rewriteScript(
    input: ScriptRewriterInput
  ): Promise<{ rewritten_script: string; changes_summary?: string }> {
    const response = await this.request<{
      output: { rewritten_script: string; changes_summary?: string };
    }>("/api/v1/ai/rewrite", {
      method: "POST",
      body: JSON.stringify(input),
    });
    return response.output;
  }

  async analyzeContent(input: { transcript: string }): Promise<ContentAnalyzerOutput> {
    const response = await this.request<{ output: ContentAnalyzerOutput }>(
      "/api/v1/ai/analyze",
      {
        method: "POST",
        body: JSON.stringify(input),
      }
    );
    return response.output;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request("/health");
  }
}

export const api = new ApiClient(API_BASE_URL);

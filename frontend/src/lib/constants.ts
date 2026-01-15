export const APP_NAME = "TranscripTok";

export const SUPPORTED_PLATFORMS = [
  { id: "tiktok", name: "TikTok", domain: "tiktok.com" },
  { id: "youtube", name: "YouTube Shorts", domain: "youtube.com" },
  { id: "instagram", name: "Instagram Reels", domain: "instagram.com" },
] as const;

export const VIDEO_QUALITIES = [
  { value: "best", label: "Best Quality" },
  { value: "720p", label: "HD (720p)" },
  { value: "480p", label: "SD (480p)" },
] as const;

export const EXPORT_FORMATS = [
  { value: "txt", label: "Text (.txt)", mime: "text/plain" },
  { value: "json", label: "JSON (.json)", mime: "application/json" },
  { value: "srt", label: "SRT Subtitles (.srt)", mime: "application/x-subrip" },
  { value: "vtt", label: "WebVTT (.vtt)", mime: "text/vtt" },
] as const;

export const HOOK_STYLES = [
  { value: "curiosity", label: "Curiosity", description: "Spark interest and intrigue" },
  { value: "shock", label: "Shock", description: "Surprising attention-grabbers" },
  { value: "question", label: "Question", description: "Thought-provoking questions" },
  { value: "story", label: "Story", description: "Compelling narrative hooks" },
] as const;

export const REWRITE_GOALS = [
  { value: "more_viral", label: "More Viral", description: "Maximize engagement" },
  { value: "shorter", label: "Shorter", description: "Condense while keeping impact" },
  { value: "clearer", label: "Clearer", description: "Improve clarity" },
] as const;

export const JOB_POLL_INTERVAL = 2000; // 2 seconds
export const MAX_POLL_ATTEMPTS = 150; // 5 minutes max

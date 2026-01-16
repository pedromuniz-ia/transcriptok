export const APP_NAME = "TranscripTok";

export const SUPPORTED_PLATFORMS = [
  { id: "tiktok", name: "TikTok", domain: "tiktok.com" },
  { id: "youtube", name: "YouTube Shorts", domain: "youtube.com" },
  { id: "instagram", name: "Instagram Reels", domain: "instagram.com" },
] as const;

export const VIDEO_QUALITIES = [
  { value: "best", label: "Melhor qualidade" },
  { value: "720p", label: "HD (720p)" },
  { value: "480p", label: "SD (480p)" },
] as const;

export const EXPORT_FORMATS = [
  { value: "txt", label: "Texto (.txt)", mime: "text/plain" },
  { value: "json", label: "JSON (.json)", mime: "application/json" },
  { value: "srt", label: "Legendas SRT (.srt)", mime: "application/x-subrip" },
  { value: "vtt", label: "Legendas WebVTT (.vtt)", mime: "text/vtt" },
] as const;

export const HOOK_STYLES = [
  { value: "curiosity", label: "Curiosidade", description: "Desperta interesse e curiosidade" },
  { value: "shock", label: "Choque", description: "Surpreendente e chamativo" },
  { value: "question", label: "Pergunta", description: "Perguntas que instigam" },
  { value: "story", label: "Historia", description: "Ganchos narrativos envolventes" },
] as const;

export const REWRITE_GOALS = [
  { value: "more_viral", label: "Mais viral", description: "Maximizar engajamento" },
  { value: "shorter", label: "Mais curto", description: "Resumir mantendo o impacto" },
  { value: "clearer", label: "Mais claro", description: "Melhorar a clareza" },
] as const;

export const JOB_POLL_INTERVAL = 2000; // 2 seconds
export const MAX_POLL_ATTEMPTS = 150; // 5 minutes max

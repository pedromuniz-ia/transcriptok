"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Copy,
  Download,
  Sparkles,
  RefreshCw,
  FileText,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { TranscriptResponse } from "@/lib/api";

interface TranscriptResultProps {
  result: {
    transcript: TranscriptResponse;
    videoInfo?: {
      title?: string;
      author?: string;
      thumbnail_url?: string;
      duration?: number;
    };
  };
}

export function TranscriptResult({ result }: TranscriptResultProps) {
  const { transcript, videoInfo } = result;
  const [showTimestamps, setShowTimestamps] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(transcript.full_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTimestamp = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const displayText = showTimestamps && transcript.segments
    ? transcript.segments
        .map((s) => `[${formatTimestamp(s.start)}] ${s.text}`)
        .join("\n")
    : transcript.full_text;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="grid md:grid-cols-2 gap-0">
            {/* Video Preview */}
            <div className="p-6 border-r border-border">
              {videoInfo?.thumbnail_url ? (
                <div className="relative aspect-[9/16] rounded-lg overflow-hidden bg-secondary mb-4">
                  <Image
                    src={videoInfo.thumbnail_url}
                    alt={videoInfo.title || "Video thumbnail"}
                    fill
                    className="object-cover"
                  />
                </div>
              ) : (
                <div className="aspect-[9/16] rounded-lg bg-secondary mb-4 flex items-center justify-center">
                  <FileText className="w-12 h-12 text-muted-foreground" />
                </div>
              )}

              <div className="space-y-2">
                {videoInfo?.title && (
                  <h3 className="font-medium line-clamp-2">{videoInfo.title}</h3>
                )}
                {videoInfo?.author && (
                  <p className="text-sm text-muted-foreground">
                    @{videoInfo.author}
                  </p>
                )}
              </div>

              <div className="flex gap-2 mt-4">
                <Button variant="secondary" size="sm" className="flex-1">
                  <Download className="w-4 h-4 mr-1" />
                  Save Cover
                </Button>
                <Button variant="secondary" size="sm" className="flex-1">
                  <Download className="w-4 h-4 mr-1" />
                  Download Video
                </Button>
              </div>
            </div>

            {/* Transcript */}
            <div className="p-6">
              {/* AI Tools Header */}
              <div className="mb-4">
                <p className="text-xs text-muted-foreground mb-2">
                  You can do more with TranscripTok AI
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm">
                    <Sparkles className="w-3 h-3 mr-1" />
                    Write hooks
                  </Button>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Rewrite scripts
                  </Button>
                  <Button variant="outline" size="sm">
                    <FileText className="w-3 h-3 mr-1" />
                    Get framework
                  </Button>
                </div>
              </div>

              {/* Transcript Controls */}
              <div className="flex items-center justify-between mb-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={showTimestamps}
                    onChange={(e) => setShowTimestamps(e.target.checked)}
                    className="rounded border-border"
                  />
                  Show timestamps
                </label>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleCopy}
                    className="h-8 w-8"
                  >
                    {copied ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Transcript Text */}
              <div className="max-h-[400px] overflow-y-auto rounded-lg bg-secondary/50 p-4">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {displayText}
                </p>
              </div>

              {/* Metadata */}
              {transcript.language && (
                <p className="mt-3 text-xs text-muted-foreground">
                  Language: {transcript.language.toUpperCase()}
                  {transcript.confidence && (
                    <> • Confidence: {(transcript.confidence * 100).toFixed(0)}%</>
                  )}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

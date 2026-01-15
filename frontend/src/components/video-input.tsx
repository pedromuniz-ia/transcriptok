"use client";

import { useState } from "react";
import { Loader2, Download } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { TranscriptResult } from "./transcript-result";
import { useTranscript } from "../hooks/use-transcript";
import { isValidVideoUrl } from "../lib/utils";

export function VideoInput() {
  const [url, setUrl] = useState("");
  const { processVideo, isLoading, result, error, reset } = useTranscript();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !isValidVideoUrl(url)) return;
    await processVideo(url);
  };

  const handleNewVideo = () => {
    reset();
    setUrl("");
  };

  if (result) {
    return (
      <div className="space-y-4">
        <TranscriptResult result={result} />
        <Button variant="outline" onClick={handleNewVideo}>
          Process Another Video
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center gap-2 p-2 rounded-xl bg-card border border-border">
        <Input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste your video link here..."
          className="flex-1 border-0 bg-transparent focus:ring-0 text-base"
          disabled={isLoading}
        />
        <Button
          type="submit"
          size="lg"
          disabled={isLoading || !url.trim() || !isValidVideoUrl(url)}
          className="shrink-0"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Download
            </>
          )}
        </Button>
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-400 text-center">{error}</p>
      )}

      {url && !isValidVideoUrl(url) && (
        <p className="mt-4 text-sm text-yellow-400 text-center">
          Please enter a valid TikTok, YouTube Shorts, or Instagram Reels URL
        </p>
      )}
    </form>
  );
}

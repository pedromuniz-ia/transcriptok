"use client";

import { useState, useCallback } from "react";
import { api, type TranscriptResponse, type JobResponse } from "@/lib/api";
import { JOB_POLL_INTERVAL, MAX_POLL_ATTEMPTS } from "@/lib/constants";

interface VideoInfo {
  title?: string;
  author?: string;
  thumbnail_url?: string;
  duration?: number;
}

interface TranscriptResult {
  transcript: TranscriptResponse;
  videoInfo?: VideoInfo;
}

export function useTranscript() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TranscriptResult | null>(null);
  const [status, setStatus] = useState<string>("");

  const pollJob = async (
    jobId: string,
    getJobFn: (id: string) => Promise<JobResponse>,
    maxAttempts: number = MAX_POLL_ATTEMPTS
  ): Promise<JobResponse> => {
    let attempts = 0;

    while (attempts < maxAttempts) {
      const job = await getJobFn(jobId);

      if (job.status === "completed") {
        return job;
      }

      if (job.status === "failed") {
        throw new Error(job.error_message || "Job failed");
      }

      attempts++;
      await new Promise((resolve) => setTimeout(resolve, JOB_POLL_INTERVAL));
    }

    throw new Error("Job timed out");
  };

  const processVideo = useCallback(async (url: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Step 1: Download video
      setStatus("Downloading video...");
      const downloadResponse = await api.downloadVideo({ url });

      // Step 2: Poll download job
      setStatus("Processing video...");
      const downloadJob = await pollJob(
        downloadResponse.job_id,
        api.getVideoJob.bind(api)
      );

      const videoInfo: VideoInfo = {
        title: downloadJob.output_data?.title as string | undefined,
        author: downloadJob.output_data?.author as string | undefined,
        thumbnail_url: downloadJob.output_data?.thumbnail_url as string | undefined,
        duration: downloadJob.output_data?.duration as number | undefined,
      };

      // Step 3: Create transcript
      setStatus("Transcribing audio...");
      const transcriptResponse = await api.createTranscript({
        job_id: downloadResponse.job_id,
      });

      // Step 4: Poll transcript job
      setStatus("Generating transcript...");
      const transcriptJob = await pollJob(
        transcriptResponse.job_id,
        api.getTranscriptJob.bind(api)
      );

      // Step 5: Get full transcript
      const transcriptId = transcriptJob.output_data?.transcript_id as string;
      const transcript = await api.getTranscript(transcriptId);

      setResult({
        transcript,
        videoInfo,
      });
      setStatus("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setStatus("");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setStatus("");
  }, []);

  return {
    processVideo,
    isLoading,
    status,
    error,
    result,
    reset,
  };
}

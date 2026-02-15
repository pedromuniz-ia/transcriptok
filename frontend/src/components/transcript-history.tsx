"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, Download, FileText, Clock, AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { api } from "../lib/api";
import type { TranscriptListItem, TranscriptListResponse } from "../lib/api";
import { formatDate, formatDuration } from "../lib/utils";

const STATUS_LABELS: Record<string, string> = {
  completed: "Concluido",
  processing: "Processando",
  failed: "Falhou",
  pending: "Pendente",
};

const PLATFORM_LABELS: Record<string, string> = {
  tiktok: "TikTok",
  youtube: "YouTube",
  instagram: "Instagram",
};

export function TranscriptHistory() {
  const [data, setData] = useState<TranscriptListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [platformFilter, setPlatformFilter] = useState<string>("");

  const fetchTranscripts = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.listTranscripts({
        limit: 50,
        search: search || undefined,
        status: statusFilter || undefined,
        platform: platformFilter || undefined,
      });
      setData(result);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, platformFilter]);

  useEffect(() => {
    const timeout = setTimeout(fetchTranscripts, 300);
    return () => clearTimeout(timeout);
  }, [fetchTranscripts]);

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const completedCount = items.filter((i) => i.job_status === "completed").length;
  const processingCount = items.filter((i) => i.job_status === "processing" || i.job_status === "pending").length;
  const failedCount = items.filter((i) => i.job_status === "failed").length;

  const cycleStatus = () => {
    const statuses = ["", "completed", "processing", "failed"];
    const idx = statuses.indexOf(statusFilter);
    setStatusFilter(statuses[(idx + 1) % statuses.length]);
  };

  const cyclePlatform = () => {
    const platforms = ["", "tiktok", "youtube", "instagram"];
    const idx = platforms.indexOf(platformFilter);
    setPlatformFilter(platforms[(idx + 1) % platforms.length]);
  };

  const mapStatus = (s?: string): "complete" | "processing" | "failed" => {
    if (s === "completed") return "complete";
    if (s === "failed") return "failed";
    return "processing";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Historico de transcricoes</h2>
          <p className="text-muted-foreground">
            Arquivo global de videos e colecoes processados
          </p>
        </div>
        <Button variant="outline" disabled>
          <Download className="w-4 h-4 mr-2" />
          Exportar tudo
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <FileText className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{total}</p>
              <p className="text-xs text-muted-foreground">Total de transcricoes</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-500/10">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{completedCount}</p>
              <p className="text-xs text-muted-foreground">Processados com sucesso</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-500/10">
              <Clock className="w-5 h-5 text-yellow-400 animate-pulse" />
            </div>
            <div>
              <p className="text-2xl font-bold">{processingCount}</p>
              <p className="text-xs text-muted-foreground">Em processamento</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-500/10">
              <AlertCircle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{failedCount}</p>
              <p className="text-xs text-muted-foreground">Falhas/Erros</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Buscar transcricoes..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={cycleStatus}>
            Status: {statusFilter ? STATUS_LABELS[statusFilter] : "Todos"}
          </Button>
          <Button variant="outline" size="sm" onClick={cyclePlatform}>
            Plataforma: {platformFilter ? PLATFORM_LABELS[platformFilter] : "Todas"}
          </Button>
        </div>
      </div>

      {/* Transcript List */}
      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="w-8 h-8 mx-auto text-muted-foreground mb-4 animate-spin" />
            <p className="text-muted-foreground">Carregando transcricoes...</p>
          </CardContent>
        </Card>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">Nenhuma transcricao ainda</h3>
            <p className="text-muted-foreground">
              Cole uma URL de video acima para comecar
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Conteudo
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Plataforma
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Data
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Duracao
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const uiStatus = mapStatus(item.job_status);
                  return (
                    <tr
                      key={item.id}
                      className="border-b border-border hover:bg-secondary/50 cursor-pointer"
                    >
                      <td className="p-4">
                        <div>
                          <p className="font-medium line-clamp-1">
                            {item.video_title || "Sem titulo"}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            @{item.video_author || "desconhecido"}
                          </p>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="secondary">
                          {PLATFORM_LABELS[item.platform ?? ""] ?? item.platform}
                        </Badge>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="p-4 text-sm">
                        {item.duration ? formatDuration(item.duration) : "-"}
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            uiStatus === "complete"
                              ? "success"
                              : uiStatus === "processing"
                              ? "warning"
                              : "destructive"
                          }
                        >
                          {uiStatus === "complete" && (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          )}
                          {STATUS_LABELS[item.job_status ?? ""] ?? item.job_status}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

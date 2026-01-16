"use client";

import { Search, Download, FileText, Clock, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";

// Mock data for demonstration
const mockStats = {
  total: 0,
  processed: "0h",
  processing: 0,
  failed: 0,
};

const mockTranscripts: Array<{
  id: string;
  title: string;
  author: string;
  platform: string;
  date: string;
  duration: string;
  status: "complete" | "processing" | "failed";
}> = [];

const STATUS_LABELS: Record<"complete" | "processing" | "failed", string> = {
  complete: "Concluido",
  processing: "Processando",
  failed: "Falhou",
};

export function TranscriptHistory() {
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
        <Button variant="outline">
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
              <p className="text-2xl font-bold">{mockStats.total}</p>
              <p className="text-xs text-muted-foreground">Total de transcricoes</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-500/10">
              <Clock className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockStats.processed}</p>
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
              <p className="text-2xl font-bold">{mockStats.processing}</p>
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
              <p className="text-2xl font-bold">{mockStats.failed}</p>
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
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Status: Todos
          </Button>
          <Button variant="outline" size="sm">
            Plataforma: Todas
          </Button>
        </div>
      </div>

      {/* Transcript List */}
      {mockTranscripts.length === 0 ? (
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
                {mockTranscripts.map((item) => (
                  <tr
                    key={item.id}
                    className="border-b border-border hover:bg-secondary/50 cursor-pointer"
                  >
                    <td className="p-4">
                      <div>
                        <p className="font-medium line-clamp-1">{item.title}</p>
                        <p className="text-sm text-muted-foreground">
                          @{item.author}
                        </p>
                      </div>
                    </td>
                    <td className="p-4">
                      <Badge variant="secondary">{item.platform}</Badge>
                    </td>
                    <td className="p-4 text-sm text-muted-foreground">
                      {item.date}
                    </td>
                    <td className="p-4 text-sm">{item.duration}</td>
                    <td className="p-4">
                      <Badge
                        variant={
                          item.status === "complete"
                            ? "success"
                            : item.status === "processing"
                            ? "warning"
                            : "destructive"
                        }
                      >
                        {item.status === "complete" && (
                          <CheckCircle className="w-3 h-3 mr-1" />
                        )}
                        {STATUS_LABELS[item.status]}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

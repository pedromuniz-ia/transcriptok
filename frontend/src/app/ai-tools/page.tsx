"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Sparkles, RefreshCw, BarChart3, Loader2 } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { HOOK_STYLES, REWRITE_GOALS } from "../../lib/constants";
import { api, type ContentAnalyzerOutput } from "../../lib/api";

type ToolTab = "hooks" | "rewrite" | "analyze";

type ToolResult =
  | { kind: "hooks"; hooks: string[] }
  | { kind: "rewrite"; text: string; summary?: string | null }
  | { kind: "analyze"; data: ContentAnalyzerOutput };

const isToolTab = (value: string | null): value is ToolTab =>
  value === "hooks" || value === "rewrite" || value === "analyze";

export default function AIToolsPage() {
  const searchParams = useSearchParams();
  const initRef = useRef(false);
  const [activeTab, setActiveTab] = useState<ToolTab>("hooks");
  const [transcript, setTranscript] = useState("");
  const [hookStyle, setHookStyle] = useState<"curiosity" | "shock" | "question" | "story">("curiosity");
  const [rewriteGoal, setRewriteGoal] = useState<"more_viral" | "shorter" | "clearer">("more_viral");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ToolResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    const storedTranscript = window.sessionStorage.getItem("ai-tools-input");
    if (storedTranscript) {
      setTranscript(storedTranscript);
    }

    const paramTool = searchParams.get("tool");
    const storedTool = window.sessionStorage.getItem("ai-tools-tab");
    const targetTab = isToolTab(paramTool) ? paramTool : isToolTab(storedTool) ? storedTool : null;
    if (targetTab) {
      setActiveTab(targetTab);
    }
  }, [searchParams]);

  const handleGenerate = async () => {
    if (!transcript.trim()) return;
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      if (activeTab === "hooks") {
        const response = await api.generateHooks({
          transcript,
          style: hookStyle,
          count: 5,
        });
        setResult({ kind: "hooks", hooks: response.hooks });
      } else if (activeTab === "rewrite") {
        const response = await api.rewriteScript({
          original_script: transcript,
          goal: rewriteGoal,
          tone: "casual",
        });
        setResult({
          kind: "rewrite",
          text: response.rewritten_script,
          summary: response.changes_summary,
        });
      } else {
        const response = await api.analyzeContent({ transcript });
        setResult({ kind: "analyze", data: response });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao gerar resposta");
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: "hooks", label: "Criar ganchos", icon: Sparkles },
    { id: "rewrite", label: "Reescrever roteiro", icon: RefreshCw },
    { id: "analyze", label: "Analisar conteudo", icon: BarChart3 },
  ] as const;

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Ferramentas de IA</h1>
          <p className="text-muted-foreground">
            Potencialize seu conteudo com ferramentas de IA
          </p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center gap-2 mb-8">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "outline"}
              onClick={() => {
                setActiveTab(tab.id);
                setResult(null);
                setError(null);
              }}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </Button>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Input */}
          <Card>
            <CardHeader>
              <CardTitle>Entrada</CardTitle>
              <CardDescription>
                {activeTab === "hooks" && "Informe sua transcricao ou tema para gerar ganchos virais"}
                {activeTab === "rewrite" && "Cole seu roteiro para receber uma versao otimizada"}
                {activeTab === "analyze" && "Cole seu conteudo para analise de viralidade"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Cole sua transcricao ou roteiro aqui..."
                className="w-full h-48 p-3 rounded-lg bg-secondary border border-border resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              />

              {activeTab === "hooks" && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Estilo de gancho</label>
                  <div className="grid grid-cols-2 gap-2">
                    {HOOK_STYLES.map((style) => (
                      <Button
                        key={style.value}
                        variant={hookStyle === style.value ? "default" : "outline"}
                        size="sm"
                        onClick={() => setHookStyle(style.value)}
                        className="justify-start"
                      >
                        {style.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "rewrite" && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Objetivo da reescrita</label>
                  <div className="grid grid-cols-3 gap-2">
                    {REWRITE_GOALS.map((goal) => (
                      <Button
                        key={goal.value}
                        variant={rewriteGoal === goal.value ? "default" : "outline"}
                        size="sm"
                        onClick={() => setRewriteGoal(goal.value)}
                      >
                        {goal.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              <Button
                onClick={handleGenerate}
                disabled={!transcript.trim() || isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Gerar
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Output */}
          <Card>
            <CardHeader>
              <CardTitle>Resultado</CardTitle>
              <CardDescription>
                {activeTab === "hooks" && "Ganchos virais gerados"}
                {activeTab === "rewrite" && "Roteiro otimizado"}
                {activeTab === "analyze" && "Analise de conteudo"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!result && !isLoading && (
                <div className="h-48 flex items-center justify-center text-muted-foreground">
                  Os resultados vao aparecer aqui
                </div>
              )}

              {isLoading && (
                <div className="h-48 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              )}

              {result?.kind === "hooks" && (
                <div className="space-y-3">
                  {result.hooks.map((hook, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-secondary border border-border hover:border-primary transition-colors cursor-pointer"
                    >
                      <span className="text-primary font-medium mr-2">{i + 1}.</span>
                      {hook}
                    </div>
                  ))}
                </div>
              )}

              {result?.kind === "rewrite" && (
                <div className="space-y-3">
                  <div className="p-4 rounded-lg bg-secondary border border-border whitespace-pre-wrap">
                    {result.text}
                  </div>
                  {result.summary && (
                    <div className="p-4 rounded-lg bg-secondary border border-border">
                      <p className="text-xs text-muted-foreground mb-2">Resumo das mudancas</p>
                      <p className="text-sm whitespace-pre-wrap">{result.summary}</p>
                    </div>
                  )}
                </div>
              )}

              {result?.kind === "analyze" && (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-secondary border border-border">
                    <p className="text-xs text-muted-foreground">Pontuacao de viralidade</p>
                    <p className="text-2xl font-bold">
                      {Math.round(result.data.virality_score)}
                    </p>
                  </div>
                  <div className="grid gap-4">
                    <div className="p-4 rounded-lg bg-secondary border border-border">
                      <p className="text-xs text-muted-foreground mb-2">Pontos fortes</p>
                      <ul className="space-y-1 text-sm">
                        {result.data.strengths.length > 0 ? (
                          result.data.strengths.map((item, index) => (
                            <li key={index}>- {item}</li>
                          ))
                        ) : (
                          <li>- Sem dados</li>
                        )}
                      </ul>
                    </div>
                    <div className="p-4 rounded-lg bg-secondary border border-border">
                      <p className="text-xs text-muted-foreground mb-2">Melhorias</p>
                      <ul className="space-y-1 text-sm">
                        {result.data.improvements.length > 0 ? (
                          result.data.improvements.map((item, index) => (
                            <li key={index}>- {item}</li>
                          ))
                        ) : (
                          <li>- Sem dados</li>
                        )}
                      </ul>
                    </div>
                    <div className="p-4 rounded-lg bg-secondary border border-border">
                      <p className="text-xs text-muted-foreground mb-2">Ganchos sugeridos</p>
                      <ul className="space-y-1 text-sm">
                        {result.data.suggested_hooks.length > 0 ? (
                          result.data.suggested_hooks.map((item, index) => (
                            <li key={index}>- {item}</li>
                          ))
                        ) : (
                          <li>- Sem dados</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {error && !isLoading && (
                <p className="mt-4 text-sm text-red-400">{error}</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

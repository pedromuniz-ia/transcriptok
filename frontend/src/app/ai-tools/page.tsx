"use client";

import { useState } from "react";
import { Sparkles, RefreshCw, BarChart3, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { HOOK_STYLES, REWRITE_GOALS } from "@/lib/constants";

export default function AIToolsPage() {
  const [activeTab, setActiveTab] = useState<"hooks" | "rewrite" | "analyze">("hooks");
  const [transcript, setTranscript] = useState("");
  const [hookStyle, setHookStyle] = useState("curiosity");
  const [rewriteGoal, setRewriteGoal] = useState("more_viral");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string[] | string | null>(null);

  const handleGenerate = async () => {
    if (!transcript.trim()) return;
    setIsLoading(true);
    setResult(null);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    if (activeTab === "hooks") {
      setResult([
        "You won't believe what happens next...",
        "This changed everything I thought I knew about...",
        "3 seconds in, my jaw dropped...",
        "Everyone is talking about this, but nobody knows...",
        "Stop scrolling! This is the secret to...",
      ]);
    } else if (activeTab === "rewrite") {
      setResult(
        "Here's your rewritten script optimized for maximum engagement and virality. The key changes focus on a stronger hook, clearer call-to-action, and better pacing for short-form video format."
      );
    }

    setIsLoading(false);
  };

  const tabs = [
    { id: "hooks", label: "Write Hooks", icon: Sparkles },
    { id: "rewrite", label: "Rewrite Script", icon: RefreshCw },
    { id: "analyze", label: "Analyze Content", icon: BarChart3 },
  ] as const;

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">AI Tools</h1>
          <p className="text-muted-foreground">
            Supercharge your content with AI-powered tools
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
              <CardTitle>Input</CardTitle>
              <CardDescription>
                {activeTab === "hooks" && "Enter your transcript or topic to generate viral hooks"}
                {activeTab === "rewrite" && "Paste your script to get an optimized version"}
                {activeTab === "analyze" && "Paste your content for virality analysis"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Paste your transcript or script here..."
                className="w-full h-48 p-3 rounded-lg bg-secondary border border-border resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              />

              {activeTab === "hooks" && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Hook Style</label>
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
                  <label className="text-sm font-medium mb-2 block">Rewrite Goal</label>
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
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Output */}
          <Card>
            <CardHeader>
              <CardTitle>Result</CardTitle>
              <CardDescription>
                {activeTab === "hooks" && "Generated viral hooks"}
                {activeTab === "rewrite" && "Optimized script"}
                {activeTab === "analyze" && "Content analysis"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!result && !isLoading && (
                <div className="h-48 flex items-center justify-center text-muted-foreground">
                  Results will appear here
                </div>
              )}

              {isLoading && (
                <div className="h-48 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              )}

              {result && Array.isArray(result) && (
                <div className="space-y-3">
                  {result.map((hook, i) => (
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

              {result && typeof result === "string" && (
                <div className="p-4 rounded-lg bg-secondary border border-border whitespace-pre-wrap">
                  {result}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

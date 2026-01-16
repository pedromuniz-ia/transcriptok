"""AI agent service using Agno framework."""

from typing import Any

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config import get_settings
from app.schemas.ai_tools import (
    AITool,
    ContentAnalyzerInput,
    ContentAnalyzerOutput,
    HookGeneratorInput,
    HookGeneratorOutput,
    HookStyle,
    RewriteGoal,
    ScriptRewriterInput,
    ScriptRewriterOutput,
)

settings = get_settings()


class AIAgentService:
    """Service for AI-powered content tools using Agno."""

    HOOK_STYLE_PROMPTS = {
        HookStyle.CURIOSITY: "Crie ganchos que despertem curiosidade e facam o publico querer saber mais",
        HookStyle.SHOCK: "Crie ganchos surpreendentes e chamativos que choquem o publico",
        HookStyle.QUESTION: "Crie perguntas instigantes que engajem o publico",
        HookStyle.STORY: "Crie ganchos que iniciem uma historia ou narrativa envolvente",
    }

    REWRITE_GOAL_PROMPTS = {
        RewriteGoal.MORE_VIRAL: "Reescreva para maximizar engajamento e compartilhamento",
        RewriteGoal.SHORTER: "Resuma mantendo a mensagem principal com impacto",
        RewriteGoal.CLEARER: "Simplifique a linguagem e aumente a clareza",
    }

    def __init__(self) -> None:
        self.model = OpenAIChat(
            id="gpt-4o-mini",
            api_key=settings.openai_api_key,
        )

    def _create_agent(self, system_prompt: str) -> Agent:
        """Create an agent with the given system prompt."""
        return Agent(
            model=self.model,
            system_message=system_prompt,
            markdown=False,
        )

    def _extract_content(self, response: Any) -> str:
        """Normalize agent responses to plain text."""
        content = response.content if hasattr(response, "content") else response
        if content is None:
            return ""
        return str(content)

    async def generate_hooks(self, input_data: HookGeneratorInput) -> HookGeneratorOutput:
        """Generate viral hooks for video content."""
        style_instruction = self.HOOK_STYLE_PROMPTS.get(
            input_data.style, self.HOOK_STYLE_PROMPTS[HookStyle.CURIOSITY]
        )

        system_prompt = f"""Voce e um criador de conteudo viral especializado em ganchos para videos curtos.
Sua tarefa e criar ganchos de abertura convincentes para videos.

{style_instruction}

Regras:
- Cada gancho deve ter no maximo 1-2 frases
- Os ganchos precisam prender a atencao nos primeiros 3 segundos
- Use palavras fortes e gatilhos emocionais
- Seja direto e impactante
- Responda apenas com os ganchos, um por linha, numerados
- Responda sempre em portugues do Brasil"""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Com base neste texto/tema, gere {input_data.count} ganchos virais:

{input_data.transcript}"""

        response = await agent.arun(user_prompt)
        content = self._extract_content(response)

        # Parse hooks from response
        hooks = self._parse_numbered_list(content)

        return HookGeneratorOutput(hooks=hooks[: input_data.count])

    async def rewrite_script(self, input_data: ScriptRewriterInput) -> ScriptRewriterOutput:
        """Rewrite script for better engagement."""
        goal_instruction = self.REWRITE_GOAL_PROMPTS.get(
            input_data.goal, self.REWRITE_GOAL_PROMPTS[RewriteGoal.MORE_VIRAL]
        )

        system_prompt = f"""Voce e um roteirista especializado em conteudo viral de videos curtos.
Sua tarefa e reescrever roteiros para maximo engajamento.

Objetivo: {goal_instruction}
Tom: {input_data.tone}

Regras:
- Mantenha a mensagem principal
- Otimize para o objetivo especificado
- Mantenha o tom informado
- Adeque para videos de 15-60 segundos
- Primeiro entregue o roteiro reescrito, depois um resumo curto das mudancas
- Responda sempre em portugues do Brasil"""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Reescreva este roteiro:

{input_data.original_script}"""

        response = await agent.arun(user_prompt)
        content = self._extract_content(response)

        # Parse response (script + optional summary)
        parts = content.split("---")
        rewritten = parts[0].strip()
        summary = parts[1].strip() if len(parts) > 1 else None

        return ScriptRewriterOutput(
            rewritten_script=rewritten,
            changes_summary=summary,
        )

    async def analyze_content(self, input_data: ContentAnalyzerInput) -> ContentAnalyzerOutput:
        """Analyze content for virality patterns."""
        system_prompt = """Voce e um analista de conteudo especializado em videos curtos virais.
Analise a transcricao para potencial de viralidade.

Formato de saida (JSON):
{
  "virality_score": <0-100>,
  "strengths": ["strength1", "strength2", ...],
  "improvements": ["improvement1", "improvement2", ...],
  "suggested_hooks": ["hook1", "hook2", ...]
}

Regras:
- Seja especifico e pratico na analise
- Responda em portugues do Brasil nos valores de texto
- Mantenha as chaves exatamente como no formato acima"""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Analise esta transcricao para viralidade:

{input_data.transcript}"""

        response = await agent.arun(user_prompt)
        content = self._extract_content(response)

        # Parse JSON response
        import json
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing
            data = {
                "virality_score": 50,
                "strengths": ["Conteudo fornecido"],
                "improvements": ["Nao foi possivel gerar uma analise detalhada"],
                "suggested_hooks": [],
            }

        return ContentAnalyzerOutput(
            virality_score=data.get("virality_score", 50),
            strengths=data.get("strengths", []),
            improvements=data.get("improvements", []),
            suggested_hooks=data.get("suggested_hooks", []),
        )

    async def run_tool(
        self, tool: AITool, input_data: Any
    ) -> HookGeneratorOutput | ScriptRewriterOutput | ContentAnalyzerOutput:
        """Run the specified AI tool."""
        if tool == AITool.HOOK_GENERATOR:
            return await self.generate_hooks(input_data)
        elif tool == AITool.SCRIPT_REWRITER:
            return await self.rewrite_script(input_data)
        elif tool == AITool.CONTENT_ANALYZER:
            return await self.analyze_content(input_data)
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _parse_numbered_list(self, text: str) -> list[str]:
        """Parse a numbered list from text."""
        import re
        lines = text.strip().split("\n")
        items = []
        for line in lines:
            # Remove numbering (1., 1), 1:, etc.)
            cleaned = re.sub(r"^\d+[\.\)\:]?\s*", "", line.strip())
            if cleaned:
                items.append(cleaned)
        return items

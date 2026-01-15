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
        HookStyle.CURIOSITY: "Create hooks that spark curiosity and make viewers want to learn more",
        HookStyle.SHOCK: "Create surprising, attention-grabbing hooks that shock the viewer",
        HookStyle.QUESTION: "Create thought-provoking questions that engage the viewer",
        HookStyle.STORY: "Create hooks that start a compelling story or narrative",
    }

    REWRITE_GOAL_PROMPTS = {
        RewriteGoal.MORE_VIRAL: "Rewrite to maximize engagement and shareability",
        RewriteGoal.SHORTER: "Condense while keeping the core message impactful",
        RewriteGoal.CLEARER: "Simplify language and improve clarity",
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

        system_prompt = f"""You are an expert viral content creator specializing in short-form video hooks.
Your task is to create compelling opening hooks for videos.

{style_instruction}

Rules:
- Each hook should be 1-2 sentences max
- Hooks must be attention-grabbing within the first 3 seconds
- Use power words and emotional triggers
- Be concise and punchy
- Output ONLY the hooks, one per line, numbered"""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Based on this transcript/topic, generate {input_data.count} viral hooks:

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

        system_prompt = f"""You are an expert video script writer specializing in viral short-form content.
Your task is to rewrite scripts for maximum engagement.

Goal: {goal_instruction}
Tone: {input_data.tone}

Rules:
- Maintain the core message
- Optimize for the specified goal
- Keep the specified tone throughout
- Make it suitable for 15-60 second videos
- First output the rewritten script, then a brief summary of changes"""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Rewrite this script:

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
        system_prompt = """You are an expert content analyst specializing in viral short-form video content.
Analyze the given transcript for virality potential.

Output format (JSON):
{
  "virality_score": <0-100>,
  "strengths": ["strength1", "strength2", ...],
  "improvements": ["improvement1", "improvement2", ...],
  "suggested_hooks": ["hook1", "hook2", ...]
}

Be specific and actionable in your analysis."""

        agent = self._create_agent(system_prompt)

        user_prompt = f"""Analyze this transcript for virality:

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
                "strengths": ["Content provided"],
                "improvements": ["Could not parse detailed analysis"],
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

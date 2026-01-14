"""AI tools schemas."""

from enum import Enum

from pydantic import BaseModel, Field


class AITool(str, Enum):
    """Available AI tools."""

    HOOK_GENERATOR = "hook_generator"
    SCRIPT_REWRITER = "script_rewriter"
    CONTENT_ANALYZER = "content_analyzer"


class HookStyle(str, Enum):
    """Hook generation styles."""

    CURIOSITY = "curiosity"
    SHOCK = "shock"
    QUESTION = "question"
    STORY = "story"


class RewriteGoal(str, Enum):
    """Script rewrite goals."""

    MORE_VIRAL = "more_viral"
    SHORTER = "shorter"
    CLEARER = "clearer"


class HookGeneratorInput(BaseModel):
    """Input for hook generator tool."""

    transcript: str = Field(..., min_length=10, max_length=10000)
    style: HookStyle = HookStyle.CURIOSITY
    count: int = Field(default=5, ge=1, le=10)


class ScriptRewriterInput(BaseModel):
    """Input for script rewriter tool."""

    original_script: str = Field(..., min_length=10, max_length=10000)
    goal: RewriteGoal = RewriteGoal.MORE_VIRAL
    tone: str = Field(default="casual", max_length=50)


class ContentAnalyzerInput(BaseModel):
    """Input for content analyzer tool."""

    transcript: str = Field(..., min_length=10, max_length=10000)


class AIToolRequest(BaseModel):
    """Request schema for AI tools."""

    tool: AITool
    input: HookGeneratorInput | ScriptRewriterInput | ContentAnalyzerInput


class HookGeneratorOutput(BaseModel):
    """Output from hook generator."""

    hooks: list[str]


class ScriptRewriterOutput(BaseModel):
    """Output from script rewriter."""

    rewritten_script: str
    changes_summary: str | None = None


class ContentAnalyzerOutput(BaseModel):
    """Output from content analyzer."""

    virality_score: float = Field(..., ge=0, le=100)
    strengths: list[str]
    improvements: list[str]
    suggested_hooks: list[str]


class AIToolResponse(BaseModel):
    """Response schema for AI tools."""

    tool: AITool
    output: HookGeneratorOutput | ScriptRewriterOutput | ContentAnalyzerOutput

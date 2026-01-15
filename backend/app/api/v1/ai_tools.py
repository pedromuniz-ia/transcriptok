"""AI tools endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import ai_tool_rate_limit
from app.schemas.ai_tools import (
    AITool,
    AIToolRequest,
    AIToolResponse,
    ContentAnalyzerInput,
    HookGeneratorInput,
    ScriptRewriterInput,
)
from app.services.ai_agent import AIAgentService

router = APIRouter()


@router.post(
    "/tools",
    response_model=AIToolResponse,
    dependencies=[Depends(ai_tool_rate_limit)],
)
async def run_ai_tool(request: AIToolRequest) -> AIToolResponse:
    """Run an AI tool on the provided input."""
    service = AIAgentService()

    try:
        # Validate input type matches tool
        if request.tool == AITool.HOOK_GENERATOR and not isinstance(
            request.input, HookGeneratorInput
        ):
            raise ValueError("Hook generator requires HookGeneratorInput")
        elif request.tool == AITool.SCRIPT_REWRITER and not isinstance(
            request.input, ScriptRewriterInput
        ):
            raise ValueError("Script rewriter requires ScriptRewriterInput")
        elif request.tool == AITool.CONTENT_ANALYZER and not isinstance(
            request.input, ContentAnalyzerInput
        ):
            raise ValueError("Content analyzer requires ContentAnalyzerInput")

        output = await service.run_tool(request.tool, request.input)

        return AIToolResponse(tool=request.tool, output=output)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI tool error: {str(e)}",
        ) from e


@router.post("/hooks", response_model=AIToolResponse)
async def generate_hooks(
    input_data: HookGeneratorInput,
) -> AIToolResponse:
    """Generate viral hooks for content."""
    service = AIAgentService()
    output = await service.generate_hooks(input_data)
    return AIToolResponse(tool=AITool.HOOK_GENERATOR, output=output)


@router.post("/rewrite", response_model=AIToolResponse)
async def rewrite_script(
    input_data: ScriptRewriterInput,
) -> AIToolResponse:
    """Rewrite script for better engagement."""
    service = AIAgentService()
    output = await service.rewrite_script(input_data)
    return AIToolResponse(tool=AITool.SCRIPT_REWRITER, output=output)


@router.post("/analyze", response_model=AIToolResponse)
async def analyze_content(
    input_data: ContentAnalyzerInput,
) -> AIToolResponse:
    """Analyze content for virality patterns."""
    service = AIAgentService()
    output = await service.analyze_content(input_data)
    return AIToolResponse(tool=AITool.CONTENT_ANALYZER, output=output)

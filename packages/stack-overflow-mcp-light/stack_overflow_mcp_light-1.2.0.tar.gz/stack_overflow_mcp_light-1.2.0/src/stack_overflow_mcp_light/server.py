"""Stack Overflow MCP Server implementation using fastmcp."""

import argparse
import os

from fastmcp import FastMCP

from stack_overflow_mcp_light.logging_config import get_logger, setup_logging
from stack_overflow_mcp_light.models.requests import (
    QuestionAnswersFetchRequest,
    QuestionsByTagRequest,
    QuestionSearchRequest,
)
from stack_overflow_mcp_light.models.responses import QuestionItem
from stack_overflow_mcp_light.tools.questions import QuestionsClient

logger = get_logger(__name__)

# Initialize MCP server
mcp: FastMCP = FastMCP("Stack Overflow MCP Server")

# Initialize specialized clients
questions_client = QuestionsClient()


@mcp.tool()
async def search_questions(request: QuestionSearchRequest) -> list[QuestionItem]:
    """
    Search Stack Overflow questions using advanced filters.

    Args:
        request: Question search request with filters and pagination

    Returns:
        List of question items
    """
    try:
        return await questions_client.search_questions(
            q=request.q,
            tagged=request.tagged,
            intitle=request.intitle,
            nottagged=request.nottagged,
            body=request.body,
            accepted=request.accepted,
            closed=request.closed,
            answers=request.answers,
            views=request.views,
            sort=request.sort.value,
            order=request.order.value,
            page=request.page,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error searching questions: {e}")
        # Return empty list in case of failure
        return []


@mcp.tool()
async def fetch_question_answers(request: QuestionAnswersFetchRequest) -> QuestionItem:
    """
    Fetch specific Stack Overflow question with its answers.

    Args:
        request: Question details request with ID and answer sorting options

    Returns:
        Question item with detailed information including answers sorted by the specified criteria with body content
    """
    try:
        return await questions_client.fetch_question_answers(
            question_id=request.question_id,
            sort=request.sort.value,
            order=request.order.value,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error getting question details: {e}")
        # Return basic question item on error
        return QuestionItem(question_id=request.question_id)


@mcp.tool()
async def search_questions_by_tag(
    request: QuestionsByTagRequest,
) -> list[QuestionItem]:
    """
    Search Stack Overflow questions that have a specific tag.

    Args:
        request: Request with tag name, sort options, and pagination

    Returns:
        List of question items with the specified tag
    """
    try:
        return await questions_client.search_questions_by_tag(
            tag=request.tag,
            sort=request.sort.value,
            order=request.order.value,
            page=request.page,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error getting questions by tag: {e}")
        # Return empty list in case of failure
        return []


def main() -> None:
    """Main entry point for the MCP server."""
    show_logs = os.getenv("STACK_OVERFLOW_MCP_SHOW_LOGS", "false").lower() == "true"
    setup_logging(include_console=show_logs)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Stack Overflow MCP Server with multiple transport support"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "http", "streamable-http", "streamable_http"],
        default="stdio",
        help="Transport type: stdio (default), sse (legacy), http/streamable-http/streamable_http (modern)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE or Streamable HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for SSE or Streamable HTTP transport (default: 0.0.0.0)",
    )

    # Parse only known args to avoid conflicts with pytest or other tools
    args, _ = parser.parse_known_args()

    # API key is optional
    api_key = os.getenv("STACK_EXCHANGE_API_KEY")
    if api_key:
        logger.info("Starting Stack Overflow MCP Server with API key...")
    else:
        logger.info(
            "Starting Stack Overflow MCP Server without API key (rate limited)..."
        )

    logger.info(f"Transport: {args.transport}")

    # Run the server with specified transport
    if args.transport == "stdio":
        mcp.run(show_banner=False)
    elif args.transport == "sse":
        logger.info(f"Starting SSE server on http://{args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port, show_banner=False)
    elif args.transport in ("http", "streamable-http", "streamable_http"):
        logger.info(f"Starting HTTP server on http://{args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port, show_banner=False)


if __name__ == "__main__":
    main()

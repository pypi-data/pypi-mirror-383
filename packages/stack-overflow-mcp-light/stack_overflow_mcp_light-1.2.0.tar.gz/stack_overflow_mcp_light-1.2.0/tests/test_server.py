"""Test suite for Stack Overflow MCP Server tools."""

from unittest.mock import patch

import pytest

from stack_overflow_mcp_light.models.requests import (
    QuestionAnswersFetchRequest,
    QuestionsByTagRequest,
    QuestionSearchRequest,
)
from stack_overflow_mcp_light.models.responses import AnswerItem, QuestionItem
from stack_overflow_mcp_light.server import mcp


@pytest.fixture
def mock_clients():
    """Create mock specialized clients."""
    with patch("stack_overflow_mcp_light.server.questions_client") as mock_questions:
        yield {"questions": mock_questions}


class TestQuestionTools:
    """Test question-related MCP tools."""

    @pytest.mark.asyncio
    async def test_search_questions(self, mock_clients):
        """Test search_questions tool."""
        mock_response = [
            QuestionItem(
                question_id=12345,
                title="How to use async/await in Python?",
                score=42,
                is_answered=True,
                link="https://stackoverflow.com/questions/12345",
            )
        ]

        # Make the mock return an awaitable (coroutine)
        async def mock_search_questions(*args, **kwargs):
            return mock_response

        mock_clients["questions"].search_questions = mock_search_questions

        request = QuestionSearchRequest(
            q="asyncio", tagged="python", page=1, page_size=10
        )
        tool_func = mcp._tool_manager._tools["search_questions"].fn
        result = await tool_func(request)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].question_id == 12345

    @pytest.mark.asyncio
    async def test_search_questions_error(self, mock_clients):
        """Test search_questions tool error handling."""
        mock_clients["questions"].search_questions.side_effect = Exception("API Error")

        request = QuestionSearchRequest(q="test")
        tool_func = mcp._tool_manager._tools["search_questions"].fn
        result = await tool_func(request)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_fetch_question_answers(self, mock_clients):
        """Test fetch_question_answers tool."""
        mock_response = QuestionItem(
            question_id=12345,
            title="Test Question",
            score=42,
            is_answered=True,
            link="https://stackoverflow.com/questions/12345",
        )
        # Set answers as extra field (allowed by model_config)
        mock_response.answers = [
            AnswerItem(
                answer_id=67890, body="Answer content", score=10, is_accepted=True
            )
        ]

        # Make the mock return an awaitable (coroutine)
        async def mock_fetch_question_answers(*args, **kwargs):
            return mock_response

        mock_clients["questions"].fetch_question_answers = mock_fetch_question_answers

        request = QuestionAnswersFetchRequest(question_id=12345)
        tool_func = mcp._tool_manager._tools["fetch_question_answers"].fn
        result = await tool_func(request)

        assert isinstance(result, QuestionItem)
        assert result.question_id == 12345
        assert result.answers is not None
        assert len(result.answers) == 1
        assert result.answers[0].answer_id == 67890
        assert result.answers[0].body == "Answer content"

    @pytest.mark.asyncio
    async def test_fetch_question_answers_with_sorting(self, mock_clients):
        """Test fetch_question_answers tool with custom sorting parameters."""
        mock_response = QuestionItem(
            question_id=12345,
            title="Test Question",
            score=42,
            is_answered=True,
            link="https://stackoverflow.com/questions/12345",
        )
        # Set answers as extra field (allowed by model_config)
        mock_response.answers = [
            AnswerItem(
                answer_id=67890, body="Answer content", score=10, is_accepted=True
            )
        ]

        # Make the mock return an awaitable (coroutine)
        async def mock_fetch_question_answers(*args, **kwargs):
            return mock_response

        mock_clients["questions"].fetch_question_answers = mock_fetch_question_answers

        from stack_overflow_mcp_light.models.requests import AnswerSort, SortOrder

        request = QuestionAnswersFetchRequest(
            question_id=12345, sort=AnswerSort.ACTIVITY, order=SortOrder.ASC
        )
        tool_func = mcp._tool_manager._tools["fetch_question_answers"].fn
        result = await tool_func(request)

        assert isinstance(result, QuestionItem)
        assert result.question_id == 12345
        assert result.answers is not None
        assert len(result.answers) == 1

    @pytest.mark.asyncio
    async def test_search_questions_by_tag(self, mock_clients):
        """Test search_questions_by_tag tool."""
        mock_response = [
            QuestionItem(
                question_id=67890,
                title="Python best practices",
                score=25,
                is_answered=True,
                link="https://stackoverflow.com/questions/67890",
            )
        ]

        # Make the mock return an awaitable (coroutine)
        async def mock_search_questions_by_tag(*args, **kwargs):
            return mock_response

        mock_clients["questions"].search_questions_by_tag = mock_search_questions_by_tag

        request = QuestionsByTagRequest(tag="python")
        tool_func = mcp._tool_manager._tools["search_questions_by_tag"].fn
        result = await tool_func(request)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].question_id == 67890


class TestServerStructure:
    """Test server structure and client usage."""

    def test_mcp_server_exists(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "_tool_manager")

    def test_all_tools_are_registered(self):
        """Test that all expected tools are properly registered."""
        tools = list(mcp._tool_manager._tools.keys())

        expected_tools = [
            "search_questions",
            "fetch_question_answers",
            "search_questions_by_tag",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not found in registered tools"

        assert len(tools) == len(
            expected_tools
        ), f"Expected {len(expected_tools)} tools, found {len(tools)}: {tools}"

    def test_error_handling_pattern(self, mock_clients):
        """Test that all tools follow the same error handling pattern."""
        mock_clients["questions"].search_questions.side_effect = Exception("Test error")
        mock_clients["questions"].fetch_question_answers.side_effect = Exception(
            "Test error"
        )

        question_search_request = QuestionSearchRequest(q="test")
        search_tool = mcp._tool_manager._tools["search_questions"].fn

        question_details_request = QuestionAnswersFetchRequest(question_id=123)
        details_tool = mcp._tool_manager._tools["fetch_question_answers"].fn

        import asyncio

        async def test_errors():
            search_result = await search_tool(question_search_request)
            details_result = await details_tool(question_details_request)

            # search_questions returns empty list on error
            assert isinstance(search_result, list)
            assert len(search_result) == 0

            # fetch_question_answers returns basic QuestionItem on error
            assert isinstance(details_result, QuestionItem)
            assert details_result.question_id == 123

        asyncio.run(test_errors())

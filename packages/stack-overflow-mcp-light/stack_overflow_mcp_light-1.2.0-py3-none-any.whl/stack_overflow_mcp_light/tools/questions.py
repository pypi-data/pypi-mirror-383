"""Questions client for Stack Exchange API operations."""

from typing import Optional

from stack_overflow_mcp_light.logging_config import get_logger
from stack_overflow_mcp_light.models.responses import AnswerItem, QuestionItem
from stack_overflow_mcp_light.tools.base_client import BaseStackExchangeClient

logger = get_logger(__name__)


class QuestionsClient(BaseStackExchangeClient):
    """Client for question-related Stack Exchange API operations."""

    def __init__(self) -> None:
        """Initialize the questions client."""
        super().__init__()

    async def search_questions(
        self,
        q: Optional[str] = None,
        tagged: Optional[str] = None,
        intitle: Optional[str] = None,
        nottagged: Optional[str] = None,
        body: Optional[str] = None,
        accepted: Optional[bool] = None,
        closed: Optional[bool] = None,
        answers: Optional[int] = None,
        views: Optional[int] = None,
        sort: str = "activity",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> list[QuestionItem]:
        """
        Search questions using advanced search parameters.

        Args:
            q: Free-form text search
            tagged: Semi-colon delimited list of tags
            intitle: Search in question titles
            nottagged: Exclude these tags
            body: Text in question body
            accepted: Has accepted answer
            closed: Question is closed
            answers: Minimum number of answers
            views: Minimum view count
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            List of question responses
        """
        params = {"sort": sort, "order": order}

        # Add search parameters if provided
        if q:
            params["q"] = q
        if tagged:
            params["tagged"] = tagged
        if intitle:
            params["intitle"] = intitle
        if nottagged:
            params["nottagged"] = nottagged
        if body:
            params["body"] = body
        if accepted is not None:
            params["accepted"] = str(accepted).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if answers is not None:
            params["answers"] = str(answers)
        if views is not None:
            params["views"] = str(views)

        try:
            # Use advanced search if we have complex parameters, otherwise basic search
            if (
                q
                or body
                or accepted is not None
                or closed is not None
                or answers
                or views
            ):
                endpoint = "/search/advanced"
            else:
                endpoint = "/search"

            logger.info(f"Searching questions with params: {params}")

            raw_response = await self._paginated_request(
                endpoint, params, page, page_size
            )

            # Transform the response to our model
            question_items = []
            if "items" in raw_response:
                for item in raw_response["items"]:
                    question_item = QuestionItem.model_validate(item)
                    question_items.append(question_item)

            return question_items

        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            raise

    async def fetch_question_answers(
        self,
        question_id: int,
        sort: str = "votes",
        order: str = "desc",
        page_size: int = 30,
    ) -> QuestionItem:
        """
        Fetch a question, including answers with body content.

        Args:
            question_id: Question ID
            sort: Sort criteria for answers ("activity", "votes", "creation")
            order: Sort order ("asc" or "desc")
            page_size: Maximum number of answers to return (1-100)

        Returns:
            QuestionItem with answers field populated with body content, sorted as requested
        """
        try:
            endpoint = f"/questions/{question_id}"

            logger.info(f"Getting question details for ID: {question_id}")

            result = await self._make_request(endpoint, {})

            if "items" not in result or len(result["items"]) == 0:
                # Return basic question item if not found
                return QuestionItem(question_id=question_id)

            question_data = result["items"][0]

            # Create question item from the basic data
            question_item = QuestionItem.model_validate(question_data)

            # Always get answers with detailed content including body
            answer_items = []

            # Get answers for the question with body content and sorting
            answers_result = await self._make_request(
                f"/questions/{question_id}/answers",
                {
                    "filter": "withbody",
                    "sort": sort,
                    "order": order,
                    "pagesize": page_size,
                },
            )

            if "items" in answers_result:
                for answer in answers_result["items"]:
                    answer_item = AnswerItem(
                        answer_id=answer.get("answer_id"),
                        is_accepted=answer.get("is_accepted"),
                        score=answer.get("score"),
                        body=answer.get("body"),
                    )
                    answer_items.append(answer_item)

            question_item.answers = answer_items

            return question_item

        except Exception as e:
            logger.error(f"Error getting question details: {e}")
            raise

    async def search_questions_by_tag(
        self,
        tag: str,
        sort: str = "activity",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> list[QuestionItem]:
        """
        Search questions that have a specific tag.

        Args:
            tag: Tag name
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            List of question items
        """
        params = {"tagged": tag, "sort": sort, "order": order}

        try:
            logger.info(f"Getting questions for tag: {tag}")

            raw_response = await self._paginated_request(
                "/questions", params, page, page_size
            )

            # Transform the response to our model
            question_items = []
            if "items" in raw_response:
                for item in raw_response["items"]:
                    question_item = QuestionItem.model_validate(item)
                    question_items.append(question_item)

            return question_items

        except Exception as e:
            logger.error(f"Error getting questions by tag: {e}")
            raise

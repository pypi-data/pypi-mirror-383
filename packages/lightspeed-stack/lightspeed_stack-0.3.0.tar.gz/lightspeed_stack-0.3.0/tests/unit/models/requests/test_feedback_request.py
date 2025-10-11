"""Unit tests for FeedbackRequest model."""

import pytest
from pydantic import ValidationError

from models.requests import FeedbackRequest, FeedbackCategory


class TestFeedbackRequest:
    """Test cases for the FeedbackRequest model."""

    def test_constructor(self) -> None:
        """Test the FeedbackRequest constructor."""
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="What is OpenStack?",
            llm_response="OpenStack is a cloud computing platform.",
            sentiment=1,
            user_feedback="This is a great response!",
        )
        assert fr.conversation_id == "123e4567-e89b-12d3-a456-426614174000"
        assert fr.user_question == "What is OpenStack?"
        assert fr.llm_response == "OpenStack is a cloud computing platform."
        assert fr.sentiment == 1
        assert fr.user_feedback == "This is a great response!"

    def test_check_invalid_uuid_format(self) -> None:
        """Test the UUID format check."""
        with pytest.raises(ValueError, match="Improper conversation ID invalid-uuid"):
            FeedbackRequest(
                conversation_id="invalid-uuid",
                user_question="What is OpenStack?",
                llm_response="OpenStack is a cloud computing platform.",
            )

    def test_check_sentiment(self) -> None:
        """Test the sentiment value check."""
        with pytest.raises(
            ValueError, match="Improper sentiment value of 99, needs to be -1 or 1"
        ):
            FeedbackRequest(
                conversation_id="123e4567-e89b-12d3-a456-426614174000",
                user_question="What is OpenStack?",
                llm_response="OpenStack is a cloud computing platform.",
                sentiment=99,  # Invalid sentiment
            )

    def test_check_feedback_provided(self) -> None:
        """Test that at least one form of feedback is provided."""
        with pytest.raises(
            ValueError, match="At least one form of feedback must be provided"
        ):
            FeedbackRequest(
                conversation_id="123e4567-e89b-12d3-a456-426614174000",
                user_question="What is OpenStack?",
                llm_response="OpenStack is a cloud computing platform.",
                sentiment=None,
                user_feedback=None,
                categories=None,
            )

    def test_feedback_too_long(self) -> None:
        """Test that user feedback is limited to 4096 characters."""
        with pytest.raises(
            ValidationError, match="should have at most 4096 characters"
        ):
            FeedbackRequest(
                conversation_id="12345678-abcd-0000-0123-456789abcdef",
                user_question="What is this?",
                llm_response="Some response",
                user_feedback="a" * 4097,
            )

    def test_with_categories(self) -> None:
        """Test FeedbackRequest with categories for negative feedback."""
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="What is Kubernetes?",
            llm_response="It's just some software thing.",
            categories=[FeedbackCategory.INCORRECT, FeedbackCategory.INCOMPLETE],
        )
        assert fr.conversation_id == "123e4567-e89b-12d3-a456-426614174000"
        assert fr.user_question == "What is Kubernetes?"
        assert fr.llm_response == "It's just some software thing."
        assert set(fr.categories) == {
            FeedbackCategory.INCORRECT,
            FeedbackCategory.INCOMPLETE,
        }
        assert fr.sentiment is None
        assert fr.user_feedback is None

    def test_with_single_category(self) -> None:
        """Test FeedbackRequest with single category for negative feedback."""
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="What is Docker?",
            llm_response="Docker is a database system.",
            categories=[FeedbackCategory.INCORRECT],
        )
        assert fr.categories == [FeedbackCategory.INCORRECT]

    def test_categories_with_duplicates(self) -> None:
        """Test that duplicate categories are removed."""
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="What is API?",
            llm_response="API is some computer thing.",
            categories=[
                FeedbackCategory.INCORRECT,
                FeedbackCategory.INCOMPLETE,
                FeedbackCategory.INCORRECT,  # Duplicate
            ],
        )
        assert len(fr.categories) == 2
        assert set(fr.categories) == {
            FeedbackCategory.INCORRECT,
            FeedbackCategory.INCOMPLETE,
        }

    def test_empty_categories_converted_to_none(self) -> None:
        """Test that empty categories list is converted to None."""
        with pytest.raises(
            ValueError, match="At least one form of feedback must be provided"
        ):
            FeedbackRequest(
                conversation_id="123e4567-e89b-12d3-a456-426614174000",
                user_question="What is testing?",
                llm_response="Testing is a verification process.",
                categories=[],  # Empty list should be converted to None
            )

    def test_categories_only_feedback(self) -> None:
        """Test that categories alone are sufficient for negative feedback."""
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="Explain machine learning",
            llm_response="It's AI stuff.",
            categories=[FeedbackCategory.NOT_RELEVANT, FeedbackCategory.INCOMPLETE],
        )
        assert fr.sentiment is None
        assert fr.user_feedback is None
        assert len(fr.categories) == 2

    def test_mixed_feedback_types(self) -> None:
        """Test FeedbackRequest with categories, sentiment, and user feedback for negative feedback."""  # pylint: disable=line-too-long
        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="What is cloud computing?",
            llm_response="It's computing in the sky.",
            sentiment=-1,
            user_feedback="This response is not informative and lacks detail",
            categories=[FeedbackCategory.OTHER, FeedbackCategory.INCOMPLETE],
        )
        assert fr.sentiment == -1
        assert fr.user_feedback == "This response is not informative and lacks detail"
        assert len(fr.categories) == 2
        assert set(fr.categories) == {
            FeedbackCategory.OTHER,
            FeedbackCategory.INCOMPLETE,
        }

    def test_all_feedback_categories(self) -> None:
        """Test that all defined feedback categories are valid."""
        all_categories = list(FeedbackCategory)

        fr = FeedbackRequest(
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            user_question="Test question",
            llm_response="Test response",
            categories=all_categories,
        )
        assert len(fr.categories) == len(all_categories)
        for category in all_categories:
            assert category in fr.categories

    def test_categories_invalid_type(self) -> None:
        """Test validation error for invalid categories type."""
        with pytest.raises(ValidationError):
            FeedbackRequest(
                conversation_id="123e4567-e89b-12d3-a456-426614174000",
                user_question="Test question",
                llm_response="Test response",
                categories="invalid_type",  # Should be list, not string
            )

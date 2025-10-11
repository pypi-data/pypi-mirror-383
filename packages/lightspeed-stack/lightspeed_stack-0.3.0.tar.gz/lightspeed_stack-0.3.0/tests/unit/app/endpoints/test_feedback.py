"""Unit tests for the /feedback REST API endpoint."""

from fastapi import HTTPException, status
import pytest

from configuration import configuration
from app.endpoints.feedback import (
    is_feedback_enabled,
    assert_feedback_enabled,
    feedback_endpoint_handler,
    store_feedback,
    update_feedback_status,
)
from models.requests import FeedbackStatusUpdateRequest
from tests.unit.utils.auth_helpers import mock_authorization_resolvers


def test_is_feedback_enabled():
    """Test that is_feedback_enabled returns True when feedback is not disabled."""
    configuration.user_data_collection_configuration.feedback_enabled = True
    assert is_feedback_enabled() is True, "Feedback should be enabled"


def test_is_feedback_disabled():
    """Test that is_feedback_enabled returns False when feedback is disabled."""
    configuration.user_data_collection_configuration.feedback_enabled = False
    assert is_feedback_enabled() is False, "Feedback should be disabled"


async def test_assert_feedback_enabled_disabled(mocker):
    """Test that assert_feedback_enabled raises HTTPException when feedback is disabled."""

    # Simulate feedback being disabled
    mocker.patch("app.endpoints.feedback.is_feedback_enabled", return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await assert_feedback_enabled(mocker.Mock())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Forbidden: Feedback is disabled"


async def test_assert_feedback_enabled(mocker):
    """Test that assert_feedback_enabled does not raise an exception when feedback is enabled."""

    # Simulate feedback being enabled
    mocker.patch("app.endpoints.feedback.is_feedback_enabled", return_value=True)

    # Should not raise an exception
    await assert_feedback_enabled(mocker.Mock())


@pytest.mark.parametrize(
    "feedback_request_data",
    [
        {},
        {
            "conversation_id": "12345678-abcd-0000-0123-456789abcdef",
            "user_question": "What is Kubernetes?",
            "llm_response": "It's some computer thing.",
            "sentiment": -1,
            "categories": ["incorrect", "incomplete"],
        },
    ],
    ids=["no_categories", "with_negative_categories"],
)
@pytest.mark.asyncio
async def test_feedback_endpoint_handler(mocker, feedback_request_data):
    """Test that feedback_endpoint_handler processes feedback for different payloads."""

    mock_authorization_resolvers(mocker)

    # Mock the dependencies
    mocker.patch("app.endpoints.feedback.assert_feedback_enabled", return_value=None)
    mocker.patch("app.endpoints.feedback.store_feedback", return_value=None)

    # Prepare the feedback request mock
    feedback_request = mocker.Mock()
    feedback_request.model_dump.return_value = feedback_request_data

    # Call the endpoint handler
    result = await feedback_endpoint_handler(
        feedback_request=feedback_request,
        _ensure_feedback_enabled=assert_feedback_enabled,
        auth=("test_user_id", "test_username", False, "test_token"),
    )

    # Assert that the expected response is returned
    assert result.response == "feedback received"


@pytest.mark.asyncio
async def test_feedback_endpoint_handler_error(mocker):
    """Test that feedback_endpoint_handler raises an HTTPException on error."""
    mock_authorization_resolvers(mocker)

    # Mock the dependencies
    mocker.patch("app.endpoints.feedback.assert_feedback_enabled", return_value=None)
    mocker.patch(
        "app.endpoints.feedback.store_feedback",
        side_effect=Exception("Error storing feedback"),
    )

    # Mock the feedback request
    feedback_request = mocker.Mock()

    # Call the endpoint handler and assert it raises an exception
    with pytest.raises(HTTPException) as exc_info:
        await feedback_endpoint_handler(
            feedback_request=feedback_request,
            _ensure_feedback_enabled=assert_feedback_enabled,
            auth=("test_user_id", "test_username", False, "test_token"),
        )

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail["response"] == "Error storing user feedback"


@pytest.mark.parametrize(
    "feedback_request_data",
    [
        {
            "conversation_id": "12345678-abcd-0000-0123-456789abcdef",
            "user_question": "What is OpenStack?",
            "llm_response": "It's some cloud thing.",
            "user_feedback": "This response is not helpful!",
            "sentiment": -1,
        },
        {
            "conversation_id": "12345678-abcd-0000-0123-456789abcdef",
            "user_question": "What is Kubernetes?",
            "llm_response": "K8s.",
            "sentiment": -1,
            "categories": ["incorrect", "not_relevant", "incomplete"],
        },
    ],
    ids=["negative_text_feedback", "negative_feedback_with_categories"],
)
def test_store_feedback(mocker, feedback_request_data):
    """Test that store_feedback correctly stores various feedback payloads."""

    configuration.user_data_collection_configuration.feedback_storage = "fake-path"

    # Patch filesystem and helpers
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("app.endpoints.feedback.Path", return_value=mocker.MagicMock())
    mocker.patch("app.endpoints.feedback.get_suid", return_value="fake-uuid")

    # Patch json to inspect stored data
    mock_json = mocker.patch("app.endpoints.feedback.json")

    user_id = "test_user_id"

    store_feedback(user_id, feedback_request_data)

    expected_data = {
        "user_id": user_id,
        "timestamp": mocker.ANY,
        **feedback_request_data,
    }

    mock_json.dump.assert_called_once_with(expected_data, mocker.ANY)


@pytest.mark.parametrize(
    "feedback_request_data",
    [
        {
            "conversation_id": "12345678-abcd-0000-0123-456789abcdef",
            "user_question": "What is OpenStack?",
            "llm_response": "It's some cloud thing.",
            "user_feedback": "This response is not helpful!",
            "sentiment": -1,
        },
        {
            "conversation_id": "12345678-abcd-0000-0123-456789abcdef",
            "user_question": "What is Kubernetes?",
            "llm_response": "K8s.",
            "sentiment": -1,
            "categories": ["incorrect", "not_relevant", "incomplete"],
        },
    ],
    ids=["negative_text_feedback", "negative_feedback_with_categories"],
)
def test_store_feedback_on_io_error(mocker, feedback_request_data):
    """Test the OSError and IOError handlings during feedback storage."""

    # non-writable path
    # avoid touching the real filesystem; simulate a permission error on open
    configuration.user_data_collection_configuration.feedback_storage = "fake-path"
    mocker.patch("app.endpoints.feedback.Path", return_value=mocker.MagicMock())
    mocker.patch("builtins.open", side_effect=PermissionError("EACCES"))

    user_id = "test_user_id"

    with pytest.raises(OSError, match="EACCES"):
        store_feedback(user_id, feedback_request_data)


async def test_update_feedback_status_different(mocker):
    """Test that update_feedback_status returns the correct status with an update."""
    configuration.user_data_collection_configuration.feedback_enabled = True

    req = FeedbackStatusUpdateRequest(status=False)
    resp = await update_feedback_status(
        req,
        auth=("test_user_id", "test_username", False, "test_token"),
    )
    assert resp.status == {
        "previous_status": True,
        "updated_status": False,
        "updated_by": "test_user_id",
        "timestamp": mocker.ANY,
    }


async def test_update_feedback_status_no_change(mocker):
    """Test that update_feedback_status returns the correct status with no update."""
    configuration.user_data_collection_configuration.feedback_enabled = True

    req = FeedbackStatusUpdateRequest(status=True)
    resp = await update_feedback_status(
        req,
        auth=("test_user_id", "test_username", False, "test_token"),
    )
    assert resp.status == {
        "previous_status": True,
        "updated_status": True,
        "updated_by": "test_user_id",
        "timestamp": mocker.ANY,
    }

from unittest.mock import MagicMock, patch
from services.llm.openai_thread import OpenAIThread

def test_message_yields_text_chunks():
    session = MagicMock()
    session.get_thread_id.return_value = None
    session.get_file_ids.return_value = []

    mock_thread = MagicMock()
    mock_thread.id = "mock-thread-id"

    # Mock message creation
    mock_message = MagicMock()

    # Mock stream generator
    mock_event = MagicMock()
    mock_event.event = "thread.message.delta"
    mock_event.data.delta.content = [
        MagicMock(type="text", text=MagicMock(value=" Hello")),
        MagicMock(type="text", text=MagicMock(value=" world"))
    ]

    with patch("services.llm.openai_thread.client") as mock_client:
        mock_client.beta.threads.create.return_value = mock_thread
        mock_client.beta.threads.messages.create.return_value = mock_message
        mock_client.beta.threads.runs.create.return_value = [mock_event]

        thread = OpenAIThread(session)
        result = list(thread.message("Test question"))

        assert result == ["Hello", "world"]
        session.set_thread_id.assert_called_once_with("mock-thread-id")
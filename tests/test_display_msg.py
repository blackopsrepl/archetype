import pytest
import streamlit as st
from src.utils import (
    display_msg,
)


class MockSessionState:
    def __init__(self):
        self.messages = []

    # Implementing dictionary-like behavior (for subscript access)
    def __getitem__(self, key):
        if key == "messages":
            return self.messages
        raise KeyError(f"{key} not found")

    def __setitem__(self, key, value):
        if key == "messages":
            self.messages = value
        else:
            raise KeyError(f"{key} not found")


@pytest.fixture
def setup_streamlit_mocks(mocker):
    # Create a mock for session_state
    mock_session_state = MockSessionState()

    # Assign this mock session state to `st.session_state`
    mocker.patch("streamlit.session_state", mock_session_state)

    # Mocking Streamlit's `chat_message` method to prevent errors during the test
    mock_chat_message = mocker.MagicMock()
    mock_chat_message.write = mocker.MagicMock()
    mocker.patch("streamlit.chat_message", return_value=mock_chat_message)


def test_display_msg(setup_streamlit_mocks):
    # Call display_msg to test its behavior
    display_msg("Hello, World!", "user")

    # Check if the message was appended to the session_state messages
    assert len(st.session_state["messages"]) == 1
    assert st.session_state["messages"][0] == {
        "role": "user",
        "content": "Hello, World!",
    }

    # Verify that st.chat_message was called and the message was written
    st.chat_message().write.assert_called_with("Hello, World!")

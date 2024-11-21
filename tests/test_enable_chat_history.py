import pytest
import streamlit as st
from src.utils import enable_chat_history
import os


class MockSessionState:
    def __init__(self):
        self._session_state = {}  # Store all keys in a dictionary

    # Implementing dictionary-like behavior (for subscript access)
    def __getitem__(self, key):
        if key in self._session_state:
            return self._session_state[key]
        raise KeyError(f"{key} not found")

    def __setitem__(self, key, value):
        self._session_state[key] = value  # Store any key-value pair

    def __delitem__(self, key):
        if key in self._session_state:
            del self._session_state[key]
        else:
            raise KeyError(f"{key} not found")

    def __contains__(self, key):
        return key in self._session_state


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

    # Set environment variable for OPENAI_API_KEY (required by the decorator)
    mocker.patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key"})


def test_enable_chat_history(setup_streamlit_mocks):
    # Ensure that the messages are initialized in session state
    st.session_state["LANGUAGE"] = "en"  # Set the language to English for testing

    # Define a dummy function to test the decorator
    @enable_chat_history
    def dummy_function():
        return "This is a test function."

    # Call the decorated function
    dummy_function()

    # Check if messages are initialized in session_state
    assert "messages" in st.session_state
    assert len(st.session_state["messages"]) > 0  # Messages should not be empty

    # Verify that the assistant's message is included in the session state
    assert st.session_state["messages"][0]["role"] == "assistant"
    assert (
        st.session_state["messages"][0]["content"]
        == "Hello, I am Clio, your personal task management assistant. How can I help you?"
    )

    # Verify that st.chat_message was called
    for msg in st.session_state["messages"]:
        st.chat_message().write.assert_any_call(msg["content"])

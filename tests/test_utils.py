import os
import pytest
import streamlit as st
from src.utils import (
    enable_chat_history,
    display_msg,
    chat_to_md,
    save_chat,
    configure_user_name,
    configure_openai_api_key,
    configure_language,
    configure_archetype,
    configure_save_checkbox,
    chatlog_append_last,
    close_existing_panels,
    StreamHandler,
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

    # Mocking Streamlit sidebar components (if necessary)
    mocker.patch("streamlit.sidebar.text_input", return_value="test")
    mocker.patch("streamlit.sidebar.selectbox", return_value="English")
    mocker.patch("streamlit.sidebar.checkbox", return_value=False)
    mocker.patch("streamlit.sidebar.button", return_value=False)


# def test_enable_chat_history(setup_streamlit_mocks):
#     @enable_chat_history
#     def dummy_function():
#         return "This is a test function."

#     with pytest.raises(SystemExit):
#         dummy_function()

#     # Check if chat history initialized
#     assert "messages" in st.session_state


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


def test_chat_to_md():
    conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]
    expected_md = "**user**: Hello\n\n**assistant**: Hi!\n\n"
    assert chat_to_md(conversation) == expected_md


def test_save_chat():
    md_text = "**user**: Hello\n\n**assistant**: Hi!\n\n"
    archetype = "THESIS"
    session_id = "12345"

    save_chat(md_text, archetype, session_id)

    file_path = f"chat-history/{archetype}_{session_id}.md"

    with open(file_path) as f:
        content = f.read()
    assert content == md_text
    os.remove(file_path)


def test_stream_handler_on_llm_new_token():
    container = st.empty()
    handler = StreamHandler(container)
    handler.on_llm_new_token("Hello ")
    assert handler.text == "Hello "

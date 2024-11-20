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


@pytest.fixture
def setup_streamlit_mocks(mocker):
    mocker.patch("streamlit.session_state", new_callable=lambda: {})
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

# def test_display_msg(setup_streamlit_mocks):
#     display_msg("Hello, World!", "user")
#     assert len(st.session_state["messages"]) == 1
#     assert st.session_state["messages"][0] == {"role": "user", "content": "Hello, World!"}


def test_chat_to_md():
    conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]
    expected_md = "**user**: Hello\n\n**assistant**: Hi!\n\n"
    assert chat_to_md(conversation) == expected_md


# def test_save_chat(tmp_path):
#     md_text = "**user**: Hello\n\n**assistant**: Hi!\n\n"
#     archetype = "THESIS"
#     session_id = "12345"

#     save_chat(md_text, archetype, session_id)

#     file_path = tmp_path / f"chat-history/{archetype}_{session_id}.md"
#     assert file_path.exists()
#     with open(file_path) as f:
#         content = f.read()
#     assert content == md_text

# def test_configure_user_name(setup_streamlit_mocks):
#     name = configure_user_name()
#     assert st.session_state["USER_NAME"] == "test"
#     assert name == "test"

# def test_configure_openai_api_key(setup_streamlit_mocks):
#     key = configure_openai_api_key()
#     assert st.session_state["OPENAI_API_KEY"] == "test"
#     assert os.environ["OPENAI_API_KEY"] == "test"

# def test_configure_language(setup_streamlit_mocks):
#     language = configure_language()
#     assert st.session_state["LANGUAGE"] == "en"
#     assert language == "en"

# def test_configure_archetype(setup_streamlit_mocks):
#     archetype = configure_archetype()
#     assert archetype == "THESIS"

# def test_configure_save_checkbox(setup_streamlit_mocks):
#     checkbox_result = configure_save_checkbox()
#     assert checkbox_result is False

# def test_chatlog_append_last(setup_streamlit_mocks):
#     st.session_state.save_chat_history = True
#     chatlog_append_last("Hello", "Hi!", "THESIS", "12345")
#     assert len(st.session_state["messages"]) == 1

# def test_close_existing_panels(setup_streamlit_mocks):
#     st.session_state.therapist_panel_open = True
#     st.session_state.admin_panel_open = True
#     close_existing_panels()
#     assert not st.session_state.therapist_panel_open
#     assert not st.session_state.admin_panel_open


def test_stream_handler_on_llm_new_token():
    container = st.empty()
    handler = StreamHandler(container)
    handler.on_llm_new_token("Hello ")
    assert handler.text == "Hello "

class MockSessionState:
    def __init__(self):
        self._session_state = {
            "messages": [],
            "USER_NAME": "test",
            "LANGUAGE": "en",
            "current_page": None,
        }

    # Implementing dictionary-like behavior (for subscript access)
    def __getitem__(self, key):
        if key in self._session_state:
            return self._session_state[key]
        raise KeyError(f"{key} not found")

    def __setitem__(self, key, value):
        self._session_state[key] = value

    def __contains__(self, key):
        return key in self._session_state

    def get(self, key, default=None):
        return self._session_state.get(key, default)


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
    mocker.patch("streamlit.sidebar.selectbox", return_value="THESIS")
    mocker.patch("streamlit.sidebar.checkbox", return_value=True)
    mocker.patch("streamlit.sidebar.button", return_value=False)


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


def test_configure_openai_api_key(setup_streamlit_mocks):
    key = configure_openai_api_key()
    assert st.session_state["OPENAI_API_KEY"] == "test"
    assert os.environ["OPENAI_API_KEY"] == "test"


def test_configure_user_name(setup_streamlit_mocks):
    # Call the function to configure the user name
    name = configure_user_name()

    # Check if the USER_NAME in session_state is correctly set to "test"
    assert st.session_state["USER_NAME"] == "test"  # Ensuring the USER_NAME is set
    assert name == "test"  # Ensure the return value is also "test"


def test_configure_language(setup_streamlit_mocks):
    language = configure_language()
    assert st.session_state["LANGUAGE"] == "en"
    assert language == "en"


def test_configure_archetype(setup_streamlit_mocks):
    archetype = configure_archetype()
    assert archetype == "THESIS"


def test_configure_save_checkbox(setup_streamlit_mocks):
    checkbox_result = configure_save_checkbox()
    assert checkbox_result is True


def test_stream_handler_on_llm_new_token():
    container = st.empty()
    handler = StreamHandler(container)
    handler.on_llm_new_token("Hello ")
    assert handler.text == "Hello "

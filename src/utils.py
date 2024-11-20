import os
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler


def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):
        ### clears chat history cache ###
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass
        ### prints chat history ###
        if "messages" not in st.session_state:
            if st.session_state["LANGUAGE"] == "en":
                st.session_state["messages"] = [
                    {
                        "role": "assistant",
                        "content": "Hello, I am Clio, your personal task management assistant. How can I help you?",
                    }
                ]
            if st.session_state["LANGUAGE"] == "it":
                st.session_state["messages"] = [
                    {
                        "role": "assistant",
                        "content": "Ciao, sono Clio, la tua assistente personale per la gestione delle attività. Come posso aiutarti?",
                    }
                ]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute


def display_msg(msg, author):
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)


def chat_to_md(conversation):
    md_text = ""
    for msg in conversation:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        md_text += f"**{role}**: {content}\n\n"
    return md_text


def save_chat(md_text, archetype, session_id):
    # save in chat-history folder too
    if not os.path.exists("chat-history"):
        os.makedirs("chat-history")
    file_name = f"chat-history/{archetype}_{session_id}.md"
    with open(file_name, "a") as f:
        f.write(md_text)


def configure_user_name():
    user_name = st.sidebar.text_input(
        label="User:",
        value=st.session_state["USER_NAME"] if "USER_NAME" in st.session_state else "",
        placeholder="Your Name",
    )
    if user_name:
        st.session_state["USER_NAME"] = user_name
    else:
        st.error("Please add your name to continue.")
        st.stop()
    return user_name


def configure_openai_api_key():
    openai_api_key = st.sidebar.text_input(
        label="OpenAI Key:",
        type="password",
        value=st.session_state["OPENAI_API_KEY"]
        if "OPENAI_API_KEY" in st.session_state
        else "",
        placeholder="sk-...",
    )
    if openai_api_key:
        st.session_state["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key
    else:
        st.error("Please add your OpenAI API key to continue.")
        st.info(
            "Obtain your key from this link: https://platform.openai.com/account/api-keys"
        )
        st.stop()
    return openai_api_key


def configure_language():
    language = st.sidebar.selectbox(
        label="Language:", options=["English", "Italian"], index=0
    )
    if language == "English":
        st.session_state["LANGUAGE"] = "en"
    elif language == "Italian":
        st.session_state["LANGUAGE"] = "it"
    return st.session_state["LANGUAGE"]


def configure_archetype():
    archetypes = ["DELPHI", "THESIS", "DIALOGOS"]
    ### TODO: implement archetype_options
    ### archetype_options = ["The Hero", "The Sage", "The Explorer", "The Rebel", "The Lover", "The Creator", "The Jester", "The Magician", "The Ruler", "The Caregiver", "The Innocent", "The Everyman"]
    archetype = st.sidebar.selectbox(label="Archetype:", options=archetypes, index=0)
    return archetype


def configure_therapist_button():
    if st.sidebar.button("👩‍⚕️ Therapist"):
        close_existing_panels()
        st.session_state.therapist_panel_open = True


def configure_admin_button():
    if st.sidebar.button("🔑 Admin"):
        close_existing_panels()
        st.session_state.admin_panel_open = True


def configure_save_checkbox():
    if st.sidebar.checkbox("💾 Save chat history"):
        st.session_state.save_chat_history = True
    else:
        st.session_state.save_chat_history = False
    return st.session_state.save_chat_history


def chatlog_append_last(user_message, assistant_message, archetype, session_id):
    if st.session_state.save_chat_history:
        md_text = chat_to_md(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )
        save_chat(md_text, archetype, session_id)


def close_existing_panels():
    if st.session_state.therapist_panel_open:
        st.session_state.therapist_panel_open = False
    if st.session_state.admin_panel_open:
        st.session_state.admin_panel_open = False


def display_admin_dashboard():
    st.sidebar.header("Admin Dashboard")
    st.sidebar.subheader("DELPHI Parameters")
    delphi_temperature = st.sidebar.slider(
        "Temperature", 0.0, 1.0, 0.0, key="delphi_temperature"
    )
    st.sidebar.subheader("DIALOGOS Parameters")
    dialogos_temperature = st.sidebar.slider(
        "Temperature", 0.0, 1.0, 0.0, key="dialogos_temperature"
    )
    st.sidebar.subheader("THESIS Parameters")
    thesis_temperature = st.sidebar.slider(
        "Temperature", 0.0, 1.0, 0.45, key="thesis_temperature"
    )
    return delphi_temperature, dialogos_temperature, thesis_temperature
    ### TODO: implement real-time sliders + archetype_options


def display_therapist_dashboard():
    pass


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text)

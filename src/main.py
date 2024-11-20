from utils import configure_language
import streamlit as st
from Archetype import archetype_factory
import utils

st.session_state["START"] = st.session_state.get("START", False)
st.set_page_config(page_title="Archetype", page_icon="🧕")
st.title("ARCHETYPE 🔗 v0.2.3")
st.write("---")


def start_app():
    st.session_state["START"] = True


if not st.session_state["START"]:
    configure_language()
    ### DESC ###
    st.write(
        "ARCHETYPE is a LLM wrapper excercise based on [langchain](https://www.langchain.com/). It aims at delivering a dynamic, multimodal chatbot within one closure."
    )

    ### INSTRUCTIONS ###
    st.header("📝 Modules:")
    st.write(
        "1. **Delphi** - allows research and information retrieval from discrete documental contexts (RAG)."
    )
    st.write(
        "2. **Dialogos** - assists the user in dealing with emotional issues and externalizing them."
    )
    st.write("3. **Thesis** - allows to plan and organize a thesis or essay project.")

    # start button that sets the app state to start
    if st.button("🚀 START"):
        start_app()
        st.rerun()
else:
    if __name__ == "__main__":
        archetype = utils.configure_archetype()
    if archetype:
        clio = archetype_factory(archetype=archetype)
        clio.main()

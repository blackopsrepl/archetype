import os, string, random
from datetime import datetime
import streamlit as st

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory, ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.utilities import WikipediaAPIWrapper
from langchain.chains import LLMChain, ConversationChain, RetrievalQA
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.vectorstores import Weaviate
from operator import itemgetter
import weaviate

import utils
from utils import StreamHandler

from prompt_templates import (
    thesis_eng,
    thesis_ita,
    dialogos_eng,
    dialogos_ita,
)


def archetype_factory(archetype):
    class Archetype:
        def __init__(self):
            utils.configure_user_name()
            utils.configure_language()
            utils.configure_openai_api_key()
            utils.configure_save_checkbox()

            if archetype == "DIALOGOS" or archetype == "THESIS":
                self.openai_model = "gpt-3.5-turbo"
                if "FIRST_DONE" not in st.session_state:
                    st.session_state["FIRST_DONE"] = False
            else:
                pass

        #####################
        ### SETUP METHODS ###
        #####################

        def setup_template(self):
            if archetype == "DIALOGOS" and st.session_state["LANGUAGE"] == "en":
                return dialogos_eng
            if archetype == "DIALOGOS" and st.session_state["LANGUAGE"] == "it":
                return dialogos_ita
            if archetype == "THESIS" and st.session_state["LANGUAGE"] == "en":
                return thesis_eng
            if archetype == "THESIS" and st.session_state["LANGUAGE"] == "it":
                return thesis_ita

        if archetype == "THESIS":

            def setup_outline(self, topic, subtopics, axes, wikipedia_research):
                if st.session_state["LANGUAGE"] == "en":
                    outline = f"\n\ncreate a summary / outline for a high school essay on {topic}, with these subtopics: \n{subtopics}.\nSubtopics must be developed and organized around these 3 axes:\n{axes}\nAlso: leverage this wikipedia research:\n{wikipedia_research}\nto help provide briefly summarized topics and subtopics.\nFormat: neat Markdown\n\n"
                if st.session_state["LANGUAGE"] == "it":
                    outline = f"\n\ncrea un sommario / outline per una tesi di maturità su {topic}, con questi sottotemi:\n{subtopics}.\nI sottotemi devono essere sviluppati e organizzati intorno a questi 3 assi:\n{axes}\nInoltre: sfrutta questa ricerca su wikipedia:\n{wikipedia_research}\nper aiutare a fornire argomenti e sottotemi brevemente riassunti.\nFormato: Markdown\n\n"
                return outline

            def setup_timeline(
                self, topic, outline, subtopics, executive_loop, start_date, end_date
            ):
                if st.session_state["LANGUAGE"] == "en":
                    timeline = f"\n\nplan a feasible linear timeline for a high school essay on {topic} with this outline:\n{outline}.\nthe essay has to be considered as the main task and it has to be broken down into subtasks.\nthe subtasks have to be organized in a feasible manner in the timeline.\nUse {subtopics} as subtasks.\nApply this additional executive loop:\n{executive_loop}\nProvide an ordered timeline of subtasks for the essay. Start date: {start_date}. Deadline: {end_date}.\nFormat: neat markdown bullet list.\n\n"
                if st.session_state["LANGUAGE"] == "it":
                    timeline = f"\n\npianifica una timeline lineare fattibile per una tesi di maturità su {topic} con questo outline:\n{outline}.\nla tesi deve essere considerata come il compito principale e deve essere scomposta in sotto-compiti.\ni sotto-compiti devono essere organizzati in modo fattibile nella timeline.\nUsa {subtopics} come sotto-compiti.\nApplica questo executive loop aggiuntivo:\n{executive_loop}\nFornisci una timeline ordinata di sotto-compiti per la tesi. Data di inizio: {start_date}. Scadenza: {end_date}.\nFormato: elenco puntato markdown.\n\n"
                return timeline

        def setup_chain(self, docsearch=None):

            if archetype == "DIALOGOS":
                t = self.setup_template()
                llm = ChatOpenAI(
                    model_name=self.openai_model, temperature=0, streaming=True
                )
                if "entity_memory" not in st.session_state:
                    st.session_state["entity_memory"] = ConversationEntityMemory(
                        llm=llm, k=50
                    )
                first_chain = LLMChain(
                    llm=llm,
                    verbose=True,
                    prompt=t["dialogos_template"],
                    memory=st.session_state.entity_memory,
                )
                second_chain = ConversationChain(
                    llm=llm,
                    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                    verbose=True,
                    memory=st.session_state.entity_memory,
                )

            if archetype == "THESIS":
                t = self.setup_template()
                executive_loop = t["executive_loop"]
                subtopics_template = t["subtopics_template"]
                axes_template = t["axes_template"]
                outline_template = t["outline_template"]
                timeline_template = t["timeline_template"]
                analysis_template = t["analysis_template"]

                ### LLM ###
                llm_dry = OpenAI(temperature=0.30, streaming=True)
                llm_verbose = ChatOpenAI(
                    model_name=self.openai_model, temperature=0.45, streaming=True
                )

                ### MEMORY ###
                memory = ConversationBufferMemory(return_messages=True)
                memory.load_memory_variables({})

                ### CHAINS ###
                subtopics_chain = (
                    RunnablePassthrough.assign(
                        memory=RunnableLambda(memory.load_memory_variables)
                        | itemgetter("history")
                    )
                    | subtopics_template
                    | llm_dry
                    | StrOutputParser()
                )
                axes_chain = (
                    RunnablePassthrough.assign(
                        memory=RunnableLambda(memory.load_memory_variables)
                        | itemgetter("history")
                    )
                    | axes_template
                    | llm_dry
                    | StrOutputParser()
                )
                outline_chain = (
                    RunnablePassthrough.assign(
                        memory=RunnableLambda(memory.load_memory_variables)
                        | itemgetter("history")
                    )
                    | outline_template
                    | llm_verbose
                    | StrOutputParser()
                )
                timeline_chain = (
                    RunnablePassthrough.assign(
                        memory=RunnableLambda(memory.load_memory_variables)
                        | itemgetter("history")
                    )
                    | timeline_template
                    | llm_dry
                    | StrOutputParser()
                )
                user_query = ""
                analysis_chain = (
                    RunnablePassthrough.assign(
                        memory=RunnableLambda(memory.load_memory_variables)
                        | itemgetter("history")
                    )
                    | analysis_template
                    | llm_verbose
                    | StrOutputParser()
                )

            if archetype == "DIALOGOS":
                return first_chain, second_chain, t
            if archetype == "THESIS":
                return (
                    subtopics_chain,
                    axes_chain,
                    outline_chain,
                    timeline_chain,
                    analysis_chain,
                    t,
                )

        @utils.enable_chat_history
        def main(self):

            if archetype == "DIALOGOS":
                if st.session_state["LANGUAGE"] == "en":
                    user_query = st.chat_input(
                        placeholder="What is causing you distress?"
                    )
                if st.session_state["LANGUAGE"] == "it":
                    user_query = st.chat_input(
                        placeholder="Cosa ti sta causando disagio?"
                    )

            if archetype == "THESIS":
                wiki = WikipediaAPIWrapper()
                if st.session_state["FIRST_DONE"] == False:
                    start_date = st.date_input("Start:")
                    end_date = st.date_input("Deadline:")
                    ### TODO: isolate date input in utils.py -> class init

                if st.session_state["LANGUAGE"] == "en":
                    user_query = st.chat_input(placeholder="Insert your thesis topic!")
                elif st.session_state["LANGUAGE"] == "it":
                    user_query = st.chat_input(
                        placeholder="Insersci l'argomento della tua tesi!"
                    )

            ####################
            ### CHAIN METHODS ##
            ####################

            if archetype == "DIALOGOS" and user_query:
                chain = self.setup_chain()
                utils.display_msg(user_query, "user")
                with st.chat_message("assistant"):
                    st_cb = StreamHandler(st.empty())
                    if "session_id" not in st.session_state:
                        st.session_state["session_id"] = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )
                    if st.session_state["FIRST_DONE"] == False:
                        ###############
                        ### PHASE 1 ###
                        ###############
                        response = chain[0].predict(topic=user_query, callbacks=[st_cb])
                        st.session_state["FIRST_DONE"] = True
                    else:
                        ###############
                        ### PHASE 2 ###
                        ###############
                        response = chain[1].predict(input=user_query, callbacks=[st_cb])
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    if st.session_state.save_chat_history == True:
                        utils.chatlog_append_last(
                            user_query,
                            response,
                            archetype,
                            st.session_state["session_id"],
                        )

            if archetype == "THESIS" and user_query:
                (
                    subtopics_chain,
                    axes_chain,
                    outline_chain,
                    timeline_chain,
                    analysis_chain,
                    t,
                ) = self.setup_chain()
                # thesis_chain, analysis_chain, t = self.setup_chain()
                utils.display_msg(user_query, "user")
                with st.chat_message("assistant"):
                    st_cb = StreamHandler(st.empty())
                    if "session_id" not in st.session_state:
                        st.session_state["session_id"] = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                    if st.session_state["FIRST_DONE"] == False:
                        ###############
                        ### PHASE 1 ###
                        ###############

                        subtopics = subtopics_chain.invoke(
                            {"topic": user_query}, config={"callbacks": [st_cb]}
                        )
                        wiki_research = wiki.run(user_query)
                        axes = axes_chain.invoke(
                            {"subtopics": subtopics}, config={"callbacks": [st_cb]}
                        )
                        outline_in = self.setup_outline(
                            topic=user_query,
                            subtopics=subtopics,
                            axes=axes,
                            wikipedia_research=wiki_research,
                        )
                        timeline_in = self.setup_timeline(
                            topic=user_query,
                            outline=outline_in,
                            subtopics=subtopics,
                            executive_loop=t["executive_loop"],
                            start_date=start_date,
                            end_date=end_date,
                        )
                        outline = outline_chain.invoke(
                            {"input": outline_in}, config={"callbacks": [st_cb]}
                        )
                        timeline = timeline_chain.invoke(
                            {"input": timeline_in}, config={"callbacks": [st_cb]}
                        )
                        response = outline + timeline
                        st.session_state["FIRST_DONE"] = True
                    else:
                        ###############
                        ### PHASE 2 ###
                        ###############
                        response = analysis_chain.invoke(
                            {"topic": user_query}, config={"callbacks": [st_cb]}
                        )
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    if st.session_state.save_chat_history == True:
                        utils.chatlog_append_last(
                            user_query,
                            response,
                            archetype,
                            st.session_state["session_id"],
                        )
                        print(st.session_state.messages)

    return Archetype()

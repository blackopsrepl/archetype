from datetime import datetime
import streamlit as st

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser

from langchain.memory import ConversationBufferMemory, ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.utilities import WikipediaAPIWrapper
from langchain.chains import LLMChain, ConversationChain, RetrievalQA
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from operator import itemgetter

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
            templates = {
                ("DIALOGOS", "en"): dialogos_eng,
                ("DIALOGOS", "it"): dialogos_ita,
                ("THESIS", "en"): thesis_eng,
                ("THESIS", "it"): thesis_ita,
            }
            return templates.get((archetype, st.session_state["LANGUAGE"]))

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

        def setup_chain(self):
            archetype_chains = {
                "DIALOGOS": lambda: self._setup_dialogos(),
                "THESIS": lambda: self._setup_thesis(),
            }

            return archetype_chains.get(archetype, lambda: None)()

        def _create_chain(self, template, llm, memory):
            return (
                RunnablePassthrough.assign(
                    memory=RunnableLambda(memory.load_memory_variables)
                    | itemgetter("history")
                )
                | template
                | llm
                | StrOutputParser()
            )

        def _setup_dialogos(self):
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
            return first_chain, second_chain, t

        def _setup_thesis(self):
            t = self.setup_template()
            executive_loop = t["executive_loop"]  # called within prompt_templates.py
            subtopics_template = t["subtopics_template"]
            axes_template = t["axes_template"]
            outline_template = t["outline_template"]
            timeline_template = t["timeline_template"]
            analysis_template = t["analysis_template"]

            llm_dry = OpenAI(temperature=0.30, streaming=True)
            llm_verbose = ChatOpenAI(
                model_name=self.openai_model, temperature=0.45, streaming=True
            )

            memory = ConversationBufferMemory(return_messages=True)
            memory.load_memory_variables({})

            subtopics_chain = self._create_chain(subtopics_template, llm_dry, memory)
            axes_chain = self._create_chain(axes_template, llm_dry, memory)
            outline_chain = self._create_chain(outline_template, llm_verbose, memory)
            timeline_chain = self._create_chain(timeline_template, llm_dry, memory)
            analysis_chain = self._create_chain(analysis_template, llm_verbose, memory)

            return (
                subtopics_chain,
                axes_chain,
                outline_chain,
                timeline_chain,
                analysis_chain,
                t,
            )

        def _handle_dialogos(self, user_query):
            chain = self.setup_chain()
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                if "session_id" not in st.session_state:
                    st.session_state["session_id"] = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )
                if not st.session_state["FIRST_DONE"]:
                    response = chain[0].predict(topic=user_query, callbacks=[st_cb])
                    st.session_state["FIRST_DONE"] = True
                else:
                    response = chain[1].predict(input=user_query, callbacks=[st_cb])

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                if st.session_state.save_chat_history:
                    utils.chatlog_append_last(
                        user_query, response, archetype, st.session_state["session_id"]
                    )

        def _handle_thesis(self, user_query, wiki, start_date, end_date):
            (
                subtopics_chain,
                axes_chain,
                outline_chain,
                timeline_chain,
                analysis_chain,
                t,
            ) = self.setup_chain()
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                if "session_id" not in st.session_state:
                    st.session_state["session_id"] = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                if not st.session_state["FIRST_DONE"]:
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
                    response = analysis_chain.invoke(
                        {"topic": user_query}, config={"callbacks": [st_cb]}
                    )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                if st.session_state.save_chat_history:
                    utils.chatlog_append_last(
                        user_query, response, archetype, st.session_state["session_id"]
                    )
                    print(st.session_state.messages)

        @utils.enable_chat_history
        def main(self):
            user_query = None

            # Get user query based on archetype
            if archetype == "DIALOGOS":
                user_query = st.chat_input(
                    placeholder="What is causing you distress?"
                    if st.session_state["LANGUAGE"] == "en"
                    else "Cosa ti sta causando disagio?"
                )
                if user_query:
                    self._handle_dialogos(user_query)

            elif archetype == "THESIS":
                wiki = WikipediaAPIWrapper()
                if not st.session_state["FIRST_DONE"]:
                    start_date = st.date_input("Start:")
                    end_date = st.date_input("Deadline:")

                user_query = st.chat_input(
                    placeholder="Insert your thesis topic!"
                    if st.session_state["LANGUAGE"] == "en"
                    else "Insersci l'argomento della tua tesi!"
                )
                if user_query:
                    self._handle_thesis(user_query, wiki, start_date, end_date)

        def _handle_dialogos(self, user_query):
            chain = self.setup_chain()
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                if "session_id" not in st.session_state:
                    st.session_state["session_id"] = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                response = (
                    chain[0].predict(topic=user_query, callbacks=[st_cb])
                    if not st.session_state["FIRST_DONE"]
                    else chain[1].predict(input=user_query, callbacks=[st_cb])
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                if st.session_state.save_chat_history:
                    utils.chatlog_append_last(
                        user_query, response, archetype, st.session_state["session_id"]
                    )

        def _handle_thesis(self, user_query, wiki, start_date, end_date):
            (
                subtopics_chain,
                axes_chain,
                outline_chain,
                timeline_chain,
                analysis_chain,
                t,
            ) = self.setup_chain()
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                if "session_id" not in st.session_state:
                    st.session_state["session_id"] = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                if not st.session_state["FIRST_DONE"]:
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
                    response = analysis_chain.invoke(
                        {"topic": user_query}, config={"callbacks": [st_cb]}
                    )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                if st.session_state.save_chat_history:
                    utils.chatlog_append_last(
                        user_query, response, archetype, st.session_state["session_id"]
                    )
                    print(st.session_state.messages)

    return Archetype()

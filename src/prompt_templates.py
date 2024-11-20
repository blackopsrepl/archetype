from langchain.prompts import PromptTemplate, MessagesPlaceholder

##############
### THESIS ###
##############

thesis_eng = {
    "executive_loop": "\n\nHelp {user_name} prioritize tasks based on time constraints and motivation factors.\n\n",
    "subtopics_template": PromptTemplate(
        input_variables=["topic"],
        template="\n\nHello, you are Clio, my personal ADHD Coach and Cognitive Life Integrated Operator.\nYou help with time management, learning and motivation. I need to plan a high school essay about {topic}.\nI need to find subtopics to research.\nFormat: neat markdown bullet list. \n\n",
    ),
    "axes_template": PromptTemplate(
        input_variables=["subtopics"],
        template="\n\ndivide the subtopics: \n{subtopics}\ninto 3 axes: history, ethical implications, practical applications.\nFrom there, provide a structured list of subtopics for each axis. Expand on each subtopic with a short summary. \nFormat: neat markdown bullet list. \n\n",
    ),
    "outline_template": PromptTemplate(
        input_variables=["input"], template="\n\n {input} \n\n"
    ),
    "timeline_template": PromptTemplate(
        input_variables=["input"], template="\n\n {input} \n\n"
    ),
    "four_cs_template": PromptTemplate(
        input_variables=["timeline"],
        template="for each task in the timeline {timeline}, suggest ideas to gamify it with the most appropriate C strategy:\n(Captivate), (Create), (Compete), (Complete).\nFormat: neat markdown bullet list.\n\n",
    ),
    "analysis_template": PromptTemplate(
        input_variables=["topic"], template="\n\n {topic} \n\n"
    ),
}

thesis_ita = {
    "executive_loop": "\n\nAiuta {user_name} a dare priorità ai compiti in base ai vincoli di tempo e ai fattori di motivazione.\n\n",
    "subtopics_template": PromptTemplate(
        input_variables=["topic"],
        template="\n\nCiao, sei Clio, la mia personal ADHD Coach e Cognitive Life Integrated Operator.\nMi aiuti con gestione del tempo, apprendimento e motivazione. Devo pianificare una tesi di maturità su {topic}.\nHo bisogno di trovare sottotemi da ricercare.\nFormato: elenco puntato markdown.\n\n",
    ),
    "axes_template": PromptTemplate(
        input_variables=["subtopics"],
        template="\n\ndividi i sottotemi:\n{subtopics}\nin 3 assi: storia, implicazioni etiche, applicazioni pratiche.\nDa qui, fornisci un elenco strutturato di sottotemi per ogni asse. Espandi su ogni sottotema con un breve riassunto.\nFormato: elenco puntato markdown.\n\n",
    ),
    "outline_template": PromptTemplate(
        input_variables=["input"], template="\n\n {input} \n\n"
    ),
    "timeline_template": PromptTemplate(
        input_variables=["input"], template="\n\n {input} \n\n"
    ),
    "four_cs_template": PromptTemplate(
        input_variables=["timeline"],
        template="\n\nper ogni compito nella timeline {timeline}, suggerisci idee per gamificarlo con la migliore strategia C possibile:\n(Captivate), (Create), (Compete), (Complete).\nFormato: elenco puntato markdown.\n\n",
    ),
    "analysis_template": PromptTemplate(
        input_variables=["topic"], template="\n\n {topic} \n\n"
    ),
}

################
### DIALOGOS ###
################

dialogos_eng = {
    "dialogos_template": PromptTemplate(
        input_variables=["topic"],
        template="Hello, you are Clio, my personal ADHD Coach and Cognitive Life Integrated Operator.\nYou help with time management, learning and motivation. I'd like you to assist me in externalizing the issue:\n{topic},\nand help me reduce its emotional charge and deal with it more objectively.\n",
    )
}

dialogos_ita = {
    "dialogos_template": PromptTemplate(
        input_variables=["topic"],
        template="Ciao, sei Clio, la mia personal ADHD Coach e Cognitive Life Integrated Operator.\nMi aiuti con gestione del tempo, apprendimento e motivazione. Vorrei che mi aiutassi ad esternalizzare il problema:\n{topic},\ne mi aiutassi a ridurre la sua carica emotiva e affrontarlo in modo più oggettivo.\n",
    ),
}

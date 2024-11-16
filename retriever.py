import os
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from generator import CodeArtifact
from dataclasses import dataclass



# Load environment variables from .env
load_dotenv()


@dataclass
class Credentials:
    repo = "Darshanroy/synthetic-data-generator"
    branch = "dev"
    github_api_url = "https://api.github.com"
    file_filter = lambda file_path: file_path.endswith((".py"))
    model = "intfloat/multilingual-e5-large"
    persist_directory = "./chroma_db"



class ConversationalRAG:
    def __init__(self, groq_api, vector_store):
        self.groq_api = groq_api
        self.llm = ChatGroq(groq_api_key=self.groq_api, model_name="Llama3-8b-8192")
        self.vector_store = vector_store

        # Initialize chat history storage
        self.chat_history_store = {}

        # Define the contextualization prompt
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Given a chat history and the latest user question 
                which might reference context in the chat history, formulate a standalone question 
                which can be understood without the chat history. Do NOT answer the question, 
                just reformulate it if needed and otherwise return it as is."""
                ),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # Define the QA prompt template
        self.qa_prompt_template = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context. 
        Think step by step before providing a detailed answer. 
        I will tip you $1000 if the user finds the answer helpful.
        <context>
        {context}
        </context>
        Question: {input}
        """)

        # Create the question-answer chain
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt_template)

        # Create the history-aware retriever
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.vector_store.as_retriever(), self.contextualize_q_prompt
        )

        # Create the retrieval chain
        self.retrieval_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)

        # Create the conversational RAG chain with chat history management
        self.conversational_rag_chain = RunnableWithMessageHistory(
            self.retrieval_chain,
            self.get_chat_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def get_chat_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Fetches the chat history for the given session."""
        if session_id not in self.chat_history_store:
            self.chat_history_store[session_id] = ChatMessageHistory()
        return self.chat_history_store[session_id]

    def ask_question(self, session_id: str, question: str):
        """Run a conversational RAG query with session-specific chat history."""
        history = self.get_chat_session_history(session_id)
        return self.conversational_rag_chain.invoke({"input": question},
    config={"configurable": {"session_id": session_id}})

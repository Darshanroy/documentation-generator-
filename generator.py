import os
import re
import time
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import GithubFileLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from dataclasses import dataclass
from getpass import getpass
from rich.console import Console
from rich.markdown import Markdown


@dataclass
class Credentials:
    repo = "Darshanroy/synthetic-data-generator"
    branch = "dev"
    github_api_url = "https://api.github.com"
    file_filter = lambda file_path: file_path.endswith((".py",'.md'))
    model = "intfloat/multilingual-e5-large"
    persist_directory = "./chroma_db"




class CodeArtifact:
    def __init__(self, repo, branch, access_token, github_api_url, file_filter, model, huggingfacehub_api_token, persist_directory):
        self.repo = repo
        self.branch = branch
        self.access_token = access_token
        self.github_api_url = github_api_url
        self.file_filter = file_filter
        self.model = model
        self.huggingfacehub_api_token = huggingfacehub_api_token
        self.persist_directory = persist_directory

    def load_documents(self):
        loader = GithubFileLoader(
            repo=self.repo,
            branch=self.branch,
            access_token=self.access_token,
            github_api_url=self.github_api_url,
            file_filter=self.file_filter
        )
        return loader.load()

    def create_embeddings(self, docs):
        embed_model = HuggingFaceEndpointEmbeddings(model=self.model, huggingfacehub_api_token=self.huggingfacehub_api_token)
        text_splitter = RecursiveCharacterTextSplitter()
        chunk_list = text_splitter.split_documents(docs)
        vector_store = Chroma.from_documents(chunk_list, embed_model, persist_directory=self.persist_directory)
        return vector_store


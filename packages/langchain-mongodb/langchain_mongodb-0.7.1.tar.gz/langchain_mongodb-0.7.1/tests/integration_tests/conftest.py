import os
import warnings
from typing import Generator, List

import pytest
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from pymongo import MongoClient

from ..utils import CONNECTION_STRING


@pytest.fixture(scope="session")
def technical_report_pages() -> List[Document]:
    """Returns a Document for each of the 100 pages of a GPT-4 Technical Report"""
    loader = PyPDFLoader("https://arxiv.org/pdf/2303.08774.pdf")
    with warnings.catch_warnings():
        # Ignore warnings raised by base class.
        warnings.simplefilter("ignore", ResourceWarning)
        pages = loader.load()
    return pages


@pytest.fixture(scope="session")
def client() -> Generator[MongoClient, None, None]:
    client = MongoClient(CONNECTION_STRING)
    yield client
    client.close()


@pytest.fixture(scope="session")
def embedding() -> Embeddings:
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIEmbeddings(
            openai_api_key=os.environ["OPENAI_API_KEY"],  # type: ignore # noqa
            model="text-embedding-3-small",
        )
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureOpenAIEmbeddings(model="text-embedding-3-small")

    return OllamaEmbeddings(model="all-minilm:l6-v2")


@pytest.fixture(scope="session")
def dimensions() -> int:
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return 1536
    return 384

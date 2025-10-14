"""Test MongoDBAtlasVectorSearch.from_documents."""

from __future__ import annotations

from typing import List

import pytest  # type: ignore[import-not-found]
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from pymongo import MongoClient
from pymongo.collection import Collection

from langchain_mongodb.index import (
    create_vector_search_index,
)

from ..utils import DB_NAME, ConsistentFakeEmbeddings, PatchedMongoDBAtlasVectorSearch

COLLECTION_NAME = "langchain_test_from_documents"
INDEX_NAME = "langchain-test-index-from-documents"
DIMENSIONS = 5


@pytest.fixture(scope="module")
def collection(client: MongoClient) -> Collection:
    if COLLECTION_NAME not in client[DB_NAME].list_collection_names():
        clxn = client[DB_NAME].create_collection(COLLECTION_NAME)
    else:
        clxn = client[DB_NAME][COLLECTION_NAME]

    clxn.delete_many({})

    if not any([INDEX_NAME == ix["name"] for ix in clxn.list_search_indexes()]):
        create_vector_search_index(
            collection=clxn,
            index_name=INDEX_NAME,
            dimensions=DIMENSIONS,
            path="embedding",
            similarity="cosine",
            wait_until_complete=60,
        )

    return clxn


@pytest.fixture(scope="module")
def example_documents() -> List[Document]:
    return [
        Document(page_content="Dogs are tough.", metadata={"a": 1}),
        Document(page_content="Cats have fluff.", metadata={"b": 1}),
        Document(page_content="What is a sandwich?", metadata={"c": 1}),
        Document(page_content="That fence is purple.", metadata={"d": 1, "e": 2}),
    ]


@pytest.fixture(scope="module")
def embeddings() -> Embeddings:
    return ConsistentFakeEmbeddings(DIMENSIONS)


@pytest.fixture(scope="module")
def vectorstore(
    collection: Collection, example_documents: List[Document], embeddings: Embeddings
) -> PatchedMongoDBAtlasVectorSearch:
    """VectorStore created with a few documents and a trivial embedding model.

    Note: PatchedMongoDBAtlasVectorSearch is MongoDBAtlasVectorSearch in all
    but one important feature. It waits until all documents are fully indexed
    before returning control to the caller.
    """
    return PatchedMongoDBAtlasVectorSearch.from_documents(
        example_documents,
        embedding=embeddings,
        collection=collection,
        index_name=INDEX_NAME,
    )


def test_default_search(
    vectorstore: PatchedMongoDBAtlasVectorSearch, example_documents: List[Document]
) -> None:
    """Test end to end construction and search."""
    output = vectorstore.similarity_search("Sandwich", k=1)
    assert len(output) == 1
    # Check for the presence of the metadata key
    assert any(
        [key.page_content == output[0].page_content for key in example_documents]
    )
    # Assert no presence of embeddings in results
    assert all(["embedding" not in key.metadata for key in output])


def test_search_with_embeddings(vectorstore: PatchedMongoDBAtlasVectorSearch) -> None:
    output = vectorstore.similarity_search("Sandwich", k=2, include_embeddings=True)
    assert len(output) == 2

    # Assert embeddings in results
    assert all([key.metadata.get("embedding") for key in output])

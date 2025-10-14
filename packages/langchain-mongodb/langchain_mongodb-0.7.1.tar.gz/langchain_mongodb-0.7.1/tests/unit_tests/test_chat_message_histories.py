import json
import warnings

import mongomock
import pytest
from langchain.memory import ConversationBufferMemory  # type: ignore[import-not-found]
from langchain_core.messages import message_to_dict
from pytest_mock import MockerFixture

from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_mongodb.utils import DRIVER_METADATA

from ..utils import MockCollection


class PatchedMongoDBChatMessageHistory(MongoDBChatMessageHistory):
    def __init__(self) -> None:
        self.session_id = "test-session"
        self.database_name = "test-database"
        self.collection_name = "test-collection"
        self.collection = MockCollection()
        self.session_id_key = "SessionId"
        self.history_key = "History"
        self.history_size = None
        self.db = self.collection.database
        self.client = self.db.client


def test_memory_with_message_store() -> None:
    """Test the memory with a message store."""
    # setup MongoDB as a message store
    message_history = PatchedMongoDBChatMessageHistory()
    with warnings.catch_warnings():
        # Ignore warnings raised by base class.
        warnings.simplefilter("ignore", DeprecationWarning)
        memory = ConversationBufferMemory(
            memory_key="baz", chat_memory=message_history, return_messages=True
        )

    # add some messages
    memory.chat_memory.add_ai_message("This is me, the AI")
    memory.chat_memory.add_user_message("This is me, the human")

    # get the message history from the memory store and turn it into a json
    messages = memory.chat_memory.messages
    messages_json = json.dumps([message_to_dict(msg) for msg in messages])

    assert "This is me, the AI" in messages_json
    assert "This is me, the human" in messages_json

    # remove the record from MongoDB, so the next test run won't pick it up
    memory.chat_memory.clear()

    assert memory.chat_memory.messages == []

    message_history.close()
    assert message_history.client.is_closed


def test_init_with_connection_string(mocker: MockerFixture) -> None:
    mock_mongo_client = mocker.patch(
        "langchain_mongodb.chat_message_histories.MongoClient"
    )

    history = MongoDBChatMessageHistory(
        connection_string="mongodb://localhost:27017/",
        session_id="test-session",
        database_name="test-database",
        collection_name="test-collection",
    )

    mock_mongo_client.assert_called_once_with(
        "mongodb://localhost:27017/",
        driver=DRIVER_METADATA,
    )
    assert history.session_id == "test-session"
    assert history.database_name == "test-database"
    assert history.collection_name == "test-collection"
    history.close()


def test_init_with_existing_client() -> None:
    client = mongomock.MongoClient()  # type: ignore[var-annotated]

    # Initialize MongoDBChatMessageHistory with the mock client
    history = MongoDBChatMessageHistory(
        connection_string=None,
        session_id="test-session",
        database_name="test-database",
        collection_name="test-collection",
        client=client,
    )

    assert history.session_id == "test-session"

    # Verify that the collection is correctly created within the specified database
    assert "test-database" in client.list_database_names()
    assert "test-collection" in client["test-database"].list_collection_names()

    history.close()


def test_init_raises_error_without_connection_or_client() -> None:
    with pytest.raises(
        ValueError, match="Either connection_string or client must be provided"
    ):
        MongoDBChatMessageHistory(
            session_id="test_session",
            connection_string=None,
            client=None,
        )


def test_init_raises_error_with_both_connection_and_client() -> None:
    client_mock = mongomock.MongoClient()  # type: ignore[var-annotated]

    with pytest.raises(
        ValueError, match="Must provide connection_string or client, not both"
    ):
        MongoDBChatMessageHistory(
            connection_string="mongodb://localhost:27017/",
            session_id="test_session",
            client=client_mock,
        )

import os
import uuid
from typing import Any, List, Union

import pytest  # type: ignore[import-not-found]
from langchain_core.caches import BaseCache
from langchain_core.globals import (
    get_llm_cache,
    set_llm_cache,
)
from langchain_core.load.dump import dumps
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, Generation, LLMResult
from pymongo import MongoClient
from pymongo.collection import Collection

from langchain_mongodb.cache import MongoDBAtlasSemanticCache, MongoDBCache
from langchain_mongodb.index import (
    create_vector_search_index,
)

from ..utils import DB_NAME, ConsistentFakeEmbeddings, FakeChatModel, FakeLLM

CONN_STRING = os.environ.get("MONGODB_URI")
INDEX_NAME = "langchain-test-index-semantic-cache"
COLLECTION = "langchain_test_cache"

DIMENSIONS = 1536  # Meets OpenAI model
TIMEOUT = 60.0


def random_string() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="module")
def collection(client: MongoClient) -> Collection:
    """A Collection with both a Vector and a Full-text Search Index"""
    if COLLECTION not in client[DB_NAME].list_collection_names():
        clxn = client[DB_NAME].create_collection(COLLECTION)
    else:
        clxn = client[DB_NAME][COLLECTION]

    clxn.delete_many({})

    if not any([INDEX_NAME == ix["name"] for ix in clxn.list_search_indexes()]):
        create_vector_search_index(
            collection=clxn,
            index_name=INDEX_NAME,
            dimensions=DIMENSIONS,
            path="embedding",
            filters=["llm_string"],
            similarity="cosine",
            wait_until_complete=TIMEOUT,
        )

    return clxn


def llm_cache(cls: Any) -> BaseCache:
    set_llm_cache(
        cls(
            embedding=ConsistentFakeEmbeddings(dimensionality=DIMENSIONS),
            connection_string=CONN_STRING,
            collection_name=COLLECTION,
            database_name=DB_NAME,
            index_name=INDEX_NAME,
            score_threshold=0.5,
            wait_until_ready=TIMEOUT,
        )
    )
    assert get_llm_cache()
    return get_llm_cache()  # type:ignore[return-value]


@pytest.fixture(scope="module", autouse=True)
def reset_cache():
    """Prevents global cache being affected in other module's tests."""
    yield
    print("\nAll cache tests have finished. Setting global cache to None.")
    set_llm_cache(None)


def _execute_test(
    prompt: Union[str, List[BaseMessage]],
    llm: Union[str, FakeLLM, FakeChatModel],
    response: List[Generation],
) -> None:
    # Fabricate an LLM String

    if not isinstance(llm, str):
        params = llm.dict()
        params["stop"] = None
        llm_string = str(sorted([(k, v) for k, v in params.items()]))
    else:
        llm_string = llm

    # If the prompt is a str then we should pass just the string
    dumped_prompt: str = prompt if isinstance(prompt, str) else dumps(prompt)

    # Update the cache
    get_llm_cache().update(dumped_prompt, llm_string, response)  # type:ignore[union-attr]

    # Retrieve the cached result through 'generate' call
    output: Union[List[Generation], LLMResult, None]
    expected_output: Union[List[Generation], LLMResult]

    if isinstance(llm, str):
        output = get_llm_cache().lookup(dumped_prompt, llm)  # type: ignore
        expected_output = response
    else:
        output = llm.generate([prompt])  # type: ignore
        expected_output = LLMResult(
            generations=[response],
            llm_output={},
        )

    # Work around older output with "usage_metadata"
    if "usage_metadata" in str(output) and "usage_metadata" not in str(expected_output):
        for generation in output.generations[0]:  # type: ignore
            generation.message.usage_metadata = None  # type: ignore

    assert output == expected_output  # type: ignore


@pytest.mark.parametrize(
    "prompt, llm, response",
    [
        ("foo", "bar", [Generation(text="fizz")]),
        ("foo", FakeLLM(), [Generation(text="fizz")]),
        (
            [HumanMessage(content="foo")],
            FakeChatModel(),
            [ChatGeneration(message=AIMessage(content="foo"))],
        ),
    ],
    ids=[
        "plain_cache",
        "cache_with_llm",
        "cache_with_chat",
    ],
)
@pytest.mark.parametrize("cacher", [MongoDBCache, MongoDBAtlasSemanticCache])
@pytest.mark.parametrize("remove_score", [True, False])
def test_mongodb_cache(
    remove_score: bool,
    cacher: Union[MongoDBCache, MongoDBAtlasSemanticCache],
    prompt: Union[str, List[BaseMessage]],
    llm: Union[str, FakeLLM, FakeChatModel],
    response: List[Generation],
    collection: Collection,
) -> None:
    llm_cache(cacher)
    if remove_score:
        get_llm_cache().score_threshold = None  # type: ignore
    try:
        _execute_test(prompt, llm, response)
    finally:
        get_llm_cache().clear()  # type:ignore[union-attr]
        get_llm_cache().close()  # type:ignore[attr-defined,union-attr]


@pytest.mark.parametrize(
    "prompts, generations",
    [
        # Single prompt, single generation
        ([random_string()], [[random_string()]]),
        # Single prompt, multiple generations
        ([random_string()], [[random_string(), random_string()]]),
        # Single prompt, multiple generations
        ([random_string()], [[random_string(), random_string(), random_string()]]),
        # Multiple prompts, multiple generations
        (
            [random_string(), random_string()],
            [[random_string()], [random_string(), random_string()]],
        ),
    ],
    ids=[
        "single_prompt_single_generation",
        "single_prompt_two_generations",
        "single_prompt_three_generations",
        "multiple_prompts_multiple_generations",
    ],
)
def test_mongodb_atlas_cache_matrix(
    prompts: List[str],
    generations: List[List[str]],
    collection: Collection,
) -> None:
    llm_cache(MongoDBAtlasSemanticCache)
    llm = FakeLLM()

    # Fabricate an LLM String
    params = llm.dict()
    params["stop"] = None
    llm_string = str(sorted([(k, v) for k, v in params.items()]))

    llm_generations = [
        [
            Generation(text=generation, generation_info=params)
            for generation in prompt_i_generations
        ]
        for prompt_i_generations in generations
    ]

    for prompt_i, llm_generations_i in zip(prompts, llm_generations):
        _execute_test(prompt_i, llm_string, llm_generations_i)
    assert llm.generate(prompts) == LLMResult(
        generations=llm_generations, llm_output={}
    )
    get_llm_cache().clear()  # type:ignore[union-attr]
    get_llm_cache().close()  # type:ignore[attr-defined,union-attr]

import inspect
from nemoguardrails.embeddings.index import EmbeddingModel, EmbeddingsIndex, IndexItem
from nemoguardrails import LLMRails, RailsConfig
from langchain.vectorstores import FAISS
from typing import List


def _get_index_name_from_id(name: str):
    if "build" in name:
        return "KnowledgeBase"
    if "bot" in name:
        return "Assistant conversations"
    if "user" in name:
        return "Human conversations"
    if "flows" in name:
        return "NeMo Conversations Flows"
    return name


def _get_model_config(config: RailsConfig, type: str):
    """Quick helper to return the config for a specific model type."""
    for model_config in config.models:
        if model_config.type == type:
            return model_config


def _split_text(document: str, meta: dict[str]) -> List[IndexItem]:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # - in our testing Character split works better with this PDF data set
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_text(document)
    items = [normalize_index_item(chunk) for chunk in chunks]
    return items


def normalize_index_item(text: str) -> IndexItem:
    ii = IndexItem(text=text, meta={})
    ii.meta["body"] = text
    return ii


class BedrockEmbeddingsIndex(EmbeddingsIndex):
    """Bedrock based embeddings index.
    `amazon titan` - embeddings.
    `faiss` -  vector store & search.
    """

    def __init__(self, embedding_model=None, embedding_engine=None, index=None):

        self._items = []
        self._embeddings = []
        self.embedding_model = embedding_model
        self.embedding_engine = embedding_engine
        self._embedding_size = 0
        self._index = index
        # if we are dealing with single purpose instance,
        # we can use the function name as the id
        self._id = inspect.currentframe().f_back.f_back.f_code.co_name
        self._loaded_from_disk = False

        self._model = init_embedding_model(embedding_model=self.embedding_model)

    @property
    def id(self):
        return self._id

    @property
    def loaded_from_disk(self):
        return self._loaded_from_disk

    @loaded_from_disk.setter
    def loaded_from_disk(self, loaded):
        """Setter to allow replacing the index dynamically."""
        self._loaded_from_disk = loaded

    @property
    def embeddings_index(self):
        return self._index

    @property
    def embedding_size(self):
        return self._embedding_size

    @property
    def embeddings(self):
        return self._embeddings

    @embeddings_index.setter
    def embeddings_index(self, index):
        """Setter to allow replacing the index dynamically."""
        self._index = index

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of texts."""

        embeddings = self._model.encode(texts)
        return embeddings

    async def add_item(self, item: IndexItem):
        """Add a single item to the index."""
        self._items.append(item)

        # If the index is already built, we skip this
        if self._index is None:
            self._embeddings.append(self._get_embeddings([item.text])[0])
            # Update the embedding if it was not computed up to this point
            self._embedding_size = len(self._embeddings[0])

    async def add_items(self, items: List[IndexItem]):

        if "build" in self._id:
            # part of the temp solution
            from . import BedrockModels

            models = BedrockModels
            models.knowledge_base = self

        """Add a list of items to the index."""
        if self._load_index_from_disk() is not None:
            self.loaded_from_disk = True
            return
        # temp value restriction for the workshop
        max_size = 49000

        # fixme: this should be fixed in the future as it might introduce a bug
        if len(items) == 1 and len(items[0].text) > max_size:
            # use _split_document to split the document into chunks
            content = items[0].text[:max_size]
            meta = items[0].meta
            items = _split_text(content, meta)

        self._items.extend(items)
        # check self._items count and if it is greater than 1

        # If the index is already built, we skip this
        if self._index is None:
            _items = [item.text for item in items]
            self._embeddings.extend(self._get_embeddings(_items))
            # Update the embedding if it was not computed up to this point
            self._embedding_size = len(self._embeddings[0])

    async def build(self):
        """Builds the vector database index."""
        index_name = _get_index_name_from_id(self._id.lower())
        try:
            if self._load_index_from_disk() is not None:
                print(f"\n{index_name} vector store index loaded from disk.")
                self.loaded_from_disk = True
                return
            print(f"\nbuilding {index_name} vector store index.")
            # iterate through the List[IndexItem] and create a list[str] of text
            texts = [item.text for item in self._items]
            # create a list of dict from List[IndexItem].meta
            metadata = [item.meta for item in self._items]

            self._index = FAISS.from_texts(
                texts, self._model.get_internal(), metadatas=metadata
            )
            # save the index to disk
            print(f"{index_name} vector store index built.")
            self._save_index_to_disk()

        except Exception as e:
            err_message = f"{e} >> Faiss _index build failed"
            # remove
            print(err_message)

    def get_index(self):
        return self._index

    async def search(self, text: str, max_results: int = 20) -> List[IndexItem]:
        """Search the closest `max_results` items."""

        query_embedding = self._get_embeddings([text])[0]
        relevant_documents = self._index.similarity_search_by_vector(query_embedding)
        docs: List[IndexItem] = []
        for doc in relevant_documents:
            # create List[IndexItem] from tuple (doc, score)
            docs.append(IndexItem(text=doc.page_content, meta=doc.metadata))
        return docs

    def _save_index_to_disk(self):
        self._index.save_local(f"./NeMo/vector_store/db_{self._id}_faiss.index")

    def _load_index_from_disk(self):
        try:
            embeddings = self._model.get_internal()
            self._index = FAISS.load_local(
                f"./NeMo/vector_store/db_{self._id}_faiss.index", embeddings
            )

        except Exception as e:
            return None

        return self._index


class BedrockEmbeddingModel(EmbeddingModel):
    """Embedding model using Amazon Bedrock."""

    def __init__(self, embeddings_model_id: str):
        self.model_id = embeddings_model_id
        from . import BedrockModels

        bedrock_models = BedrockModels
        self.model = bedrock_models.get_embeddings(
            embeddings_model_id=embeddings_model_id
        )
        self.embeddings = None
        self.embedding_size = len(self.encode(["test"])[0])
        # print(f"embedding_size - {self.embedding_size}")

    def get_internal(self):
        return self.model

    def encode(self, documents: List[str]) -> List[List[float]]:
        # Make embedding request to Bedrock API
        embeddings = self.model.embed_documents(documents)
        return embeddings


def init_embedding_model(embedding_model: str) -> BedrockEmbeddingModel:
    """Initialize the embedding model."""
    return BedrockEmbeddingModel(embedding_model)

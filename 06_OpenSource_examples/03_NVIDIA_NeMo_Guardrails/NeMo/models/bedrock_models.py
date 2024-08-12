from langchain.embeddings import BedrockEmbeddings
from utils import bedrock
from langchain.llms.bedrock import Bedrock
import os


class BedrockClientSingleton:
    # Singleton instance attributes, initially set to None.
    _instance = None
    _embeddings_model = None
    _model_id = "anthropic.claude-v2"  # Default model ID, can be replaced with 'anthropic.claude-instant-v1'.
    _embeddings_model_id = "amazon.titan-embed-text-v1"  # Default embeddings model ID.
    _llm = None  # Large Language Model (LLM) instance.
    _knowledge_base = (
        None  # Placeholder for a knowledge base that might be used with the LLM.
    )
    _bedrock_client = None  # The Bedrock API client instance.

    @property
    def knowledge_base(self):
        return self._knowledge_base

    @knowledge_base.setter
    def knowledge_base(self, knowledge_base):
        self._knowledge_base = knowledge_base

    @property
    def llm(self):
        return self._llm

    @llm.setter
    def llm(self, llm):
        self._llm = llm

    def init_bedrock_client(self, client):
        """
        Initializes the Bedrock client.

        Args:
            client: An optional pre-configured Bedrock client. If not provided, a default client will be initialized.

        """

        if self._bedrock_client is not None and client is None:
            return

        if client is not None:
            self._bedrock_client = client
            return

        self._bedrock_client = bedrock.get_bedrock_client(
            assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
            region=os.environ.get("AWS_DEFAULT_REGION", None),
            runtime=True,
        )

    def init_llm(self, model_id):
        """
        Initializes the LLM with the specified model ID.

        Args:
            model_id: Optional model ID to use. If not provided, the default model ID is used.
        """
        if model_id is not None:
            self._model_id = model_id

        model_parameter = {}

        self._llm = Bedrock(
            model_id=self._model_id,
            client=self._bedrock_client,
            model_kwargs=model_parameter,
        )

    def get_embeddings(self, embeddings_model_id: str):
        """
        Retrieves the embeddings model based on the provided model ID.

        Args:
            embeddings_model_id: The model ID for the embeddings model to retrieve.

        Returns:
            An instance of the BedrockEmbeddings class initialized with the specified model ID.
        """
        self.init_bedrock_client(None)

        if embeddings_model_id:
            self._embeddings_model_id = embeddings_model_id

        if self._embeddings_model is None:
            self._embeddings_model = BedrockEmbeddings(
                model_id=self._embeddings_model_id, client=self._bedrock_client
            )

        return self._embeddings_model


# Instantiation of the BedrockClientSingleton which can be used throughout the code.
BedrockModels = BedrockClientSingleton()

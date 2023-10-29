from langchain.embeddings import BedrockEmbeddings
from utils import bedrock
from langchain.llms.bedrock import Bedrock
import os


class BedrockClientSingleton:
    _instance = None
    _embeddings_model = None
    _model_id = 'anthropic.claude-v2' #'anthropic.claude-instant-v1'
    _embeddings_model_id = 'amazon.titan-embed-text-v1'
    _llm = None
    _knowledge_base = None
    _bedrock_client = None

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

    # enable bedrock client external injection and configuration
    # if client is None, then we will use the default bedrock client
    def init_bedrock_client(self, client):

        if self._bedrock_client is not None and client is None:
            return

        if client is not None:
            self._bedrock_client = client
            return

        self._bedrock_client = bedrock.get_bedrock_client(
            assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
            region=os.environ.get("AWS_DEFAULT_REGION", None),
            runtime=True
        )

    def init_llm(self, model_id):

        if model_id is not None:
            self._model_id = model_id

        model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}

        self._llm = Bedrock(
            model_id=self._model_id,
            client=self._bedrock_client,
            model_kwargs=model_parameter,
        )

    def get_embeddings(self, embeddings_model_id: str):
        self.init_bedrock_client(None)

        if embeddings_model_id:
            self._embeddings_model_id = embeddings_model_id

        if self._embeddings_model is None:
            self._embeddings_model = BedrockEmbeddings(
                model_id=self._embeddings_model_id,
                client=self._bedrock_client)

        return self._embeddings_model

BedrockModels = BedrockClientSingleton()
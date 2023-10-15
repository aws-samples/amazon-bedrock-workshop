from langchain.embeddings import BedrockEmbeddings
from utils import bedrock

import os


class BedrockBorgModels(object):
    """
    Borg singleton embeddings provider.
    """
    _we_are_one = {}
    _embeddings_model = None
    _model_id = ""
    _llm = None
    _knowledge_base = None

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._we_are_one
        return self

    @property
    def llm(self):
        return self._llm

    @llm.setter
    def llm(self, llm):
        self._llm = llm

    @property
    def knowledge_base(self):
        return self._knowledge_base

    @knowledge_base.setter
    def knowledge_base(self, knowledge_base):
        self._knowledge_base = knowledge_base

    def get_embeddings(self, model_id: str = "amazon.titan-embed-g1-text-02"):
        if model_id:
            self._model_id = model_id

        if self._embeddings_model is None:
            boto3_bedrock = bedrock.get_bedrock_client(
                assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
                region=os.environ.get("AWS_DEFAULT_REGION", None),
                runtime=True
            )
            self._embeddings_model = BedrockEmbeddings(
                model_id=self._model_id,
                client=boto3_bedrock)
        return self._embeddings_model


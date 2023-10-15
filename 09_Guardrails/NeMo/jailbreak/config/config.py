from nemoguardrails import LLMRails
from nemoguardrails.llm.providers import register_llm_provider

import sys, os




def init(app: LLMRails):

    for path in sys.path:
        if "guardrails" in path.lower():
            sys.path.append(os.path.join(path, 'NeMo'))
            break

    from models import (
        BedrockLLM, BedrockBorgModels, BedrockEmbeddingsIndex,
        bedrock_output_moderation, bedrock_check_jailbreak, bedrock_v2_parser, bedrock_claude_v2_parser
    )

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    _bedrockBorgModels = BedrockBorgModels()
    app.register_filter(bedrock_v2_parser, name="bedrock_v2")
    app.register_filter(bedrock_claude_v2_parser, name="bedrock_claude_v2")
    # Custom Actions
    app.register_action(bedrock_check_jailbreak, name="bedrock_check_jailbreak")
    app.register_action(bedrock_output_moderation, name="bedrock_output_moderation")


    # Custom LLM Provider
    register_llm_provider("amazon_bedrock", BedrockLLM)
    # Custom Embedding Search Providers
    # You can implement your own custom embedding search provider by subclassing EmbeddingsIndex.
    # For quick reference, the complete interface is included below:
    # https://github.com/NVIDIA/NeMo-Guardrails/blob/main/docs/user_guide/advanced/embedding-search-providers.md



    borg_models = BedrockBorgModels()
    borg_models.get_embeddings(model_id="amazon.titan-embed-text-v1")
    app.register_embedding_search_provider("amazon_bedrock_embedding", BedrockEmbeddingsIndex)


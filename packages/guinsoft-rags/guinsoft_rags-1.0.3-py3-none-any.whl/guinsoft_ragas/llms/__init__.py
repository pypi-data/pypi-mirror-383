from guinsoft_ragas.llms.base import RagasLLM
from guinsoft_ragas.llms.langchain import LangchainLLM
from guinsoft_ragas.llms.llamaindex import LlamaIndexLLM
from guinsoft_ragas.llms.openai import OpenAI

__all__ = ["RagasLLM", "LangchainLLM", "LlamaIndexLLM", "llm_factory", "OpenAI"]


def llm_factory(model="gpt-4-1106-preview") -> RagasLLM:
    return OpenAI(model=model)

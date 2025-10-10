"""LangChain integration."""

from typing import Optional, Type, Any
from pydantic import BaseModel, Field


class RAGURLTool:
    """
    LangChain tool for RAG URL processing.

    Usage:
        >>> from rag_url_agent.integrations.langchain import RAGURLTool
        >>> from langchain.agents import initialize_agent
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> tool = RAGURLTool()
        >>> agent = initialize_agent([tool], ChatOpenAI(), agent="zero-shot-react")
        >>> agent.run("Process https://example.com and summarize")
    """

    name = "rag_url_processor"
    description = """Process URLs and answer questions about their content.
    Commands: add:<url>, query:<question>, list"""

    def __init__(self, llm: str = "ollama", **kwargs):
        from rag_url_agent import SimpleAgent
        self.agent = SimpleAgent(llm=llm, **kwargs)

    def _run(self, query: str) -> str:
        """Execute tool."""
        query = query.strip()

        if query.startswith("add:"):
            url = query[4:].strip()
            result = self.agent.add(url)
            return f"✓ Added: {result.get('title', url)}" if result['success'] else f"✗ Error: {result.get('error')}"

        elif query.startswith("query:"):
            return self.agent.ask(query[6:].strip())

        elif query == "list":
            urls = self.agent.list()
            return "\n".join([f"- {u['title']}" for u in urls]) if urls else "No URLs"

        return self.agent.ask(query)

    def run(self, query: str) -> str:
        """LangChain compatibility."""
        return self._run(query)


def as_langchain_tool(llm: str = "ollama", **kwargs):
    """
    Convert to LangChain BaseTool (requires langchain installed).

    Usage:
        >>> from rag_url_agent.integrations.langchain import as_langchain_tool
        >>> tool = as_langchain_tool("ollama")
    """
    try:
        from langchain.tools import BaseTool
        from langchain.callbacks.manager import CallbackManagerForToolRun

        class _LangChainTool(BaseTool):
            name = "rag_url_processor"
            description = "Process URLs and answer questions"

            def __init__(self):
                super().__init__()
                from rag_url_agent import SimpleAgent
                self.agent = SimpleAgent(llm=llm, **kwargs)

            def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
                tool = RAGURLTool(llm=llm, **kwargs)
                return tool._run(query)

            async def _arun(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
                return self._run(query, run_manager)

        return _LangChainTool()

    except ImportError:
        raise ImportError("LangChain not installed. Run: pip install langchain")
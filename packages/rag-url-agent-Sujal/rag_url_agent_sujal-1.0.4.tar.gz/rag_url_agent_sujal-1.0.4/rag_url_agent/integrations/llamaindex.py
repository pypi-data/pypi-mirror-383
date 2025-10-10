"""LlamaIndex integration."""

from typing import Optional, Any


class RAGURLQueryEngine:
    """
    LlamaIndex query engine.

    Usage:
        >>> from rag_url_agent.integrations.llamaindex import RAGURLQueryEngine
        >>>
        >>> engine = RAGURLQueryEngine()
        >>> engine.add_url("https://example.com")
        >>> response = engine.query("What is this?")
    """

    def __init__(self, llm: str = "ollama", **kwargs):
        from rag_url_agent import SimpleAgent
        self.agent = SimpleAgent(llm=llm, **kwargs)

    def add_url(self, url: str):
        """Add URL to knowledge base."""
        return self.agent.add(url)

    def query(self, query: str) -> str:
        """Query the engine."""
        return self.agent.ask(query)

    async def aquery(self, query: str) -> str:
        """Async query."""
        return self.query(query)


def as_llamaindex_tool(llm: str = "ollama", **kwargs):
    """
    Convert to LlamaIndex tool.

    Usage:
        >>> from rag_url_agent.integrations.llamaindex import as_llamaindex_tool
        >>> tool = as_llamaindex_tool("ollama")
    """
    try:
        from llama_index.core.tools import FunctionTool

        engine = RAGURLQueryEngine(llm=llm, **kwargs)

        def process_url(command: str) -> str:
            """Process URL command: 'add:<url>' or 'query:<question>'"""
            if command.startswith("add:"):
                result = engine.add_url(command[4:].strip())
                return f"Added: {result.get('title', 'URL')}"
            elif command.startswith("query:"):
                return engine.query(command[6:].strip())
            return engine.query(command)

        return FunctionTool.from_defaults(
            fn=process_url,
            name="rag_url_processor",
            description="Process URLs and answer questions"
        )

    except ImportError:
        raise ImportError("LlamaIndex not installed. Run: pip install llama-index")
"""
Research tools for information retrieval and content extraction.

These tools enable agents to search the web, fetch content, and extract
information from various sources without using LLMs.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from ..types import ToolResult
from ._base import BaseTool

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import arxiv  # type: ignore

    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False


class WebSearchTool(BaseTool):
    """Search the web using Tavily API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
    ) -> None:
        super().__init__(
            name="web_search",
            description=(
                "Search the web for information. Returns titles, URLs, and snippets from search results. "
                "Results are filtered based on allowed/blocked domain rules for security."
            ),
        )
        self.api_key = api_key
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query string"},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                },
            },
            "required": ["query"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        if not HTTPX_AVAILABLE:
            return ToolResult(
                success=False,
                result=None,
                error="httpx not installed. Install with: pip install httpx",
                metadata={},
            )

        query = parameters["query"]
        max_results = parameters.get("max_results", 5)

        if not self.api_key:
            return ToolResult(
                success=False,
                result=None,
                error="Tavily API key not provided. Pass api_key to WebSearchTool constructor.",
                metadata={"query": query},
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": max_results,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

            results = []
            for item in data.get("results", []):
                url = item.get("url", "")

                # Apply domain filtering
                if self._is_domain_allowed(url):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": url,
                            "snippet": item.get("content", ""),
                        }
                    )

            return ToolResult(
                success=True,
                result=results,
                error=None,
                metadata={
                    "query": query,
                    "count": len(results),
                    "filtered": len(data.get("results", [])) - len(results),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Web search failed: {str(e)}",
                metadata={"query": query},
            )

    def _is_domain_allowed(self, url: str) -> bool:
        """
        Check if URL passes domain filtering rules.

        Args:
            url: URL to check

        Returns:
            True if URL is allowed, False otherwise
        """
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc.lower()

            # Check blocked domains first
            if self.blocked_domains:
                for blocked in self.blocked_domains:
                    blocked_lower = blocked.lower()
                    # Match exact domain or subdomain (ends with .blocked_domain)
                    if domain == blocked_lower or domain.endswith("." + blocked_lower):
                        return False

            # If allowed_domains is specified, only allow those
            if self.allowed_domains:
                for allowed in self.allowed_domains:
                    allowed_lower = allowed.lower()
                    # Match exact domain or subdomain (ends with .allowed_domain)
                    if domain == allowed_lower or domain.endswith("." + allowed_lower):
                        return True
                return False  # Not in allowed list

            # No restrictions or passed all checks
            return True
        except Exception:
            # If parsing fails, be conservative and block
            return False


class WebFetchTool(BaseTool):
    """Fetch content from a URL."""

    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
        max_content_length: int = 100000,
    ) -> None:
        super().__init__(
            name="web_fetch",
            description=(
                "Fetch the HTML content from a URL. Returns the raw HTML or text content. "
                "URL access is filtered based on allowed/blocked domain rules for security. "
                "Content is truncated if it exceeds maximum length."
            ),
        )
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
        self.max_content_length = max_content_length

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "extract_text": {
                    "type": "boolean",
                    "description": "If true, extract only text content (requires beautifulsoup4)",
                },
            },
            "required": ["url"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        if not HTTPX_AVAILABLE:
            return ToolResult(
                success=False,
                result=None,
                error="httpx not installed. Install with: pip install httpx",
                metadata={},
            )

        url = parameters["url"]
        extract_text = parameters.get("extract_text", False)

        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")

            # Check domain filtering
            if not self._is_domain_allowed(url):
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"URL domain is blocked or not in allowed list: {parsed_url.netloc}",
                    metadata={"url": url, "domain": parsed_url.netloc},
                )

            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()

            content = response.text

            # Truncate content if too long
            was_truncated = False
            if len(content) > self.max_content_length:
                content = content[: self.max_content_length]
                was_truncated = True

            if extract_text and BS4_AVAILABLE:
                soup = BeautifulSoup(content, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                content = "\n".join(line for line in lines if line)

            return ToolResult(
                success=True,
                result=content,
                error=None,
                metadata={
                    "url": url,
                    "content_length": len(content),
                    "status_code": response.status_code,
                    "truncated": was_truncated,
                    "max_length": self.max_content_length,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to fetch URL: {str(e)}",
                metadata={"url": url},
            )

    def _is_domain_allowed(self, url: str) -> bool:
        """
        Check if URL passes domain filtering rules.

        Args:
            url: URL to check

        Returns:
            True if URL is allowed, False otherwise
        """
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc.lower()

            # Check blocked domains first
            if self.blocked_domains:
                for blocked in self.blocked_domains:
                    blocked_lower = blocked.lower()
                    # Match exact domain or subdomain (ends with .blocked_domain)
                    if domain == blocked_lower or domain.endswith("." + blocked_lower):
                        return False

            # If allowed_domains is specified, only allow those
            if self.allowed_domains:
                for allowed in self.allowed_domains:
                    allowed_lower = allowed.lower()
                    # Match exact domain or subdomain (ends with .allowed_domain)
                    if domain == allowed_lower or domain.endswith("." + allowed_lower):
                        return True
                return False  # Not in allowed list

            # No restrictions or passed all checks
            return True
        except Exception:
            # If parsing fails, be conservative and block
            return False


class ExtractTextTool(BaseTool):
    """Extract clean text content from HTML."""

    def __init__(self) -> None:
        super().__init__(
            name="extract_text",
            description="Extract clean text content from HTML, removing scripts, styles, and tags.",
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "html": {
                    "type": "string",
                    "description": "HTML content to extract text from",
                },
                "selector": {
                    "type": "string",
                    "description": "Optional CSS selector to extract specific elements",
                },
            },
            "required": ["html"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        if not BS4_AVAILABLE:
            return ToolResult(
                success=False,
                result=None,
                error="beautifulsoup4 not installed. Install with: pip install beautifulsoup4",
                metadata={},
            )

        html = parameters["html"]
        selector = parameters.get("selector")

        try:
            soup = BeautifulSoup(html, "html.parser")

            if selector:
                elements = soup.select(selector)
                if not elements:
                    raise ValueError(f"No elements found matching selector: {selector}")
                text_parts = [elem.get_text(strip=True) for elem in elements]
                text = "\n\n".join(text_parts)
            else:
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                text = "\n".join(line for line in lines if line)

            return ToolResult(
                success=True,
                result=text,
                error=None,
                metadata={"length": len(text), "selector": selector},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Text extraction failed: {str(e)}",
                metadata={},
            )


class ArxivSearchTool(BaseTool):
    """Search arXiv for academic papers."""

    def __init__(self) -> None:
        super().__init__(
            name="arxiv_search",
            description="Search arXiv for academic papers. Returns titles, authors, abstracts, and PDF URLs.",
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (can use arXiv query syntax)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["relevance", "lastUpdatedDate", "submittedDate"],
                    "description": "Sort order for results (default: relevance)",
                },
            },
            "required": ["query"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        if not ARXIV_AVAILABLE:
            return ToolResult(
                success=False,
                result=None,
                error="arxiv package not installed. Install with: pip install arxiv",
                metadata={},
            )

        query = parameters["query"]
        max_results = parameters.get("max_results", 5)
        sort_by_str = parameters.get("sort_by", "relevance")

        try:
            sort_by_map = {
                "relevance": arxiv.SortCriterion.Relevance,
                "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
                "submittedDate": arxiv.SortCriterion.SubmittedDate,
            }
            sort_by = sort_by_map.get(sort_by_str, arxiv.SortCriterion.Relevance)

            search = arxiv.Search(query=query, max_results=max_results, sort_by=sort_by)

            results = []
            for paper in search.results():
                results.append(
                    {
                        "title": paper.title,
                        "authors": [author.name for author in paper.authors],
                        "abstract": paper.summary,
                        "pdf_url": paper.pdf_url,
                        "published": paper.published.isoformat(),
                        "arxiv_id": paper.entry_id.split("/")[-1],
                    }
                )

            return ToolResult(
                success=True,
                result=results,
                error=None,
                metadata={"query": query, "count": len(results)},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"arXiv search failed: {str(e)}",
                metadata={"query": query},
            )


def create_research_tools(tavily_api_key: Optional[str] = None) -> Sequence[BaseTool]:
    """
    Create a list of research tools for information retrieval.

    Args:
        tavily_api_key: Optional API key for Tavily web search

    Returns:
        List of research tool instances

    Raises:
        ImportError: If required dependencies are not installed
    """
    tools: List[BaseTool] = []

    if HTTPX_AVAILABLE:
        tools.append(WebSearchTool(api_key=tavily_api_key))
        tools.append(WebFetchTool())

    if BS4_AVAILABLE:
        tools.append(ExtractTextTool())

    if ARXIV_AVAILABLE:
        tools.append(ArxivSearchTool())

    if not tools:
        raise ImportError(
            "No research tools available. Install dependencies with: "
            "pip install httpx beautifulsoup4 arxiv"
        )

    return tools

# === Web Explorer ===
import asyncio
import hashlib
import re
from typing import NewType, TypeVar

import aiohttp
import structlog
from bs4 import BeautifulSoup
from cachetools import TTLCache
from playwright.async_api import Browser, async_playwright
from playwright_stealth import Stealth

from aiwebexplorer.agents import evaluate_request_agent, extraction_agent, finalizer_agent
from aiwebexplorer.interfaces import AgentInterfaceError, IAgent, IResponse

logger = structlog.get_logger()


class WebExplorerResponse(IResponse[str]):
    """Response object for WebExplorer results."""

    def __init__(self, content: str):
        self._content = content

    @property
    def content(self) -> str:
        return self._content


HTMLContent: NewType = str
TextContent: NewType = str

T = TypeVar("T")


class WebExplorer(IAgent[T]):
    """Optimized web explorer for fast information extraction from web pages."""

    # Default site selectors (can be overridden via constructor)
    DEFAULT_SITE_SELECTORS = {
        "amazon": 'div[id="ppd"]',
        "ebay": 'div[id="mainContent"]',
        "etsy": 'div[class*="listing-page"]',
        "craigslist": 'section[class="body"]',
    }

    # Tags to always exclude for faster processing
    DEFAULT_EXCLUDE_TAGS = [
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "video",
        "audio",
        "canvas",
        "map",
        "object",
        "embed",
    ]

    # TTL cache for web exploration results
    _cache: TTLCache = TTLCache(maxsize=1000, ttl=1800)  # 30 minutes TTL, 1000 max items

    # Shared browser instance
    _browser: Browser | None = None
    _browser_lock = asyncio.Lock()

    max_parallel_processing = 8

    def __init__(
        self,
        exclude_tags: list[str] | None = None,
        css_selector: str | None = None,
        max_content_length: int = 5000,
        use_lightweight_fetch: bool = True,  # Try lightweight fetch first
        site_selectors: dict[str, str] | None = None,  # Site-specific CSS selectors
        _evaluate_request_agent: IAgent[str] | None = None,
        _extraction_agent: IAgent[str] | None = None,
        _finalizer_agent: IAgent[str] | None = None,
    ):
        """Initialize WebExplorer.

        Args:
            exclude_tags: Additional HTML tags to exclude from processing
            css_selector: Custom CSS selector to use for content extraction
            max_content_length: Maximum content length for LLM processing
            use_lightweight_fetch: Whether to try lightweight HTTP fetch first
            site_selectors: Dictionary mapping site names to CSS selectors
        """
        self.exclude_tags = (exclude_tags or []) + self.DEFAULT_EXCLUDE_TAGS
        self.css_selector = css_selector
        self.max_content_length = max_content_length
        self.use_lightweight_fetch = use_lightweight_fetch
        self.site_selectors = site_selectors or self.DEFAULT_SITE_SELECTORS.copy()

        self._evaluation_agent: IAgent[str] = _evaluate_request_agent or evaluate_request_agent
        self._extractor_agent: IAgent[str] = _extraction_agent or extraction_agent
        self._finalizer_agent: IAgent[str] = _finalizer_agent or finalizer_agent

    async def arun(self, prompt: str) -> IResponse[str]:
        """Run web exploration based on the prompt.

        The prompt should contain the URL and question in a structured format.
        Expected format: "URL: <url> Question: <question> [Browser: true/false]"

        Args:
            prompt: The exploration prompt containing URL and question

        Returns:
            WebExplorerResponse containing the extracted information
        """

        logger.debug("WebExplorer arun called", prompt=prompt)

        response = await self._evaluation_agent.arun(prompt)

        result = self._extract_result(response.content)
        if result == "ERROR":
            error_message = self._extract_message(response.content)
            raise AgentInterfaceError(error_message)

        logger.debug("Evaluation agent response", response=response.content)
        url = self._extract_url(response.content)

        if url is None:
            error_message = f"""
            Evaluation agent is supposed to return the URL of the website where the search will be performed. 
            No URL found in the response.
            Response: {response.content}
            """
            raise AgentInterfaceError(error_message)

        site_type = self._detect_site_type(url)
        logger.info("Detected site type", site_type=site_type)
        logger.info("Starting HTML content extraction")
        html_content = await self._get_html_content(url)
        logger.info("HTML content extraction completed")
        logger.info("Starting Text content extraction")
        text_content = await self._extract_from_html(html_content, site_type, url)
        logger.info("Text content extraction completed")
        keywords = self._extract_keywords(response.content)
        question = self._extract_question(response.content)
        logger.info("Keywords extracted", keywords=keywords)
        logger.info("Question extracted", question=question)
        chunks = self._split_text_content(text_content)
        logger.info("Text content split into chunks", total_chunks=len(chunks))
        extracted_result = await self._try_extraction(
            question, content=chunks, keywords=keywords, parallel_number_of_chunks=4, partial_result=response.content
        )
        logger.info("Extraction completed", result=extracted_result)

        # Use finalizer agent to synthesize the extracted information into a proper answer
        finalizer_prompt = f"Question: {question}\n\nExtracted Information:\n{extracted_result}"
        finalizer_response = await self._finalizer_agent.arun(finalizer_prompt)
        logger.info("Finalization completed", result=finalizer_response.content)

        return WebExplorerResponse(finalizer_response.content)

    def _split_text_content(self, text: str, *, chunk_size: int = 6000, overlap: int = 30) -> list[str]:
        """Split the text content into chunks."""
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

    def _reduce_window(self, chunk: str, keywords: list[str], *, window_size: int = 400) -> str:
        """Reduce chunk size by focusing on 200 characters before and after each keyword."""
        if not keywords:
            return chunk

        reduced_parts = []
        chunk_lower = chunk.lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            start = 0
            while True:
                # Find keyword occurrence
                pos = chunk_lower.find(keyword_lower, start)
                if pos == -1:
                    break

                # Calculate window boundaries
                window_start = max(0, pos - window_size)
                window_end = min(len(chunk), pos + len(keyword) + window_size)

                # Extract window content
                window_content = chunk[window_start:window_end]
                reduced_parts.append(window_content)

                # Move search position past this occurrence
                start = pos + len(keyword)

        if not reduced_parts:
            return chunk

        # Join all windows and remove duplicates while preserving order
        seen = set()
        unique_parts = []
        for part in reduced_parts:
            if part not in seen:
                seen.add(part)
                unique_parts.append(part)

        return " ... ".join(unique_parts)

    def _extract_message(self, text: str) -> str:
        """Extract the message from the text."""
        match = re.search(r"\[MESSAGE\]: (.*)", text)
        if match:
            return match.group(1)
        raise AgentInterfaceError("No [MESSAGE] found in the response")

    def _extract_keywords(self, text: str) -> list[str]:
        """Keywords from the text."""
        # Keywords are defined in the following format: "Keywords: key1, key2, key3"
        match = re.search(r"\[KEYWORDS\]:\s*(.*?)(?=\s*\[|\s*$)", text, re.MULTILINE | re.DOTALL)
        if match:
            keywords = match.group(1).strip().split(",")
            return [keyword.strip() for keyword in keywords]
        return []

    def _extract_url(self, text: str) -> str:
        """Extract the URL from the text."""
        match = re.search(r"\[URL\]:\s*(https?://[^\s]+)", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        raise AgentInterfaceError("No [URL] found in the response")

    def _extract_question(self, text: str) -> str:
        """Extract the question from the text."""
        match = re.search(r"\[QUESTION\]:\s*(.*?)(?=\s*\[|\s*$)", text, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()
        raise AgentInterfaceError("No [QUESTION] found in the response")

    def _extract_result(self, text: str) -> str:
        """Extract the result from the text."""
        # More robust regex that handles newlines and whitespace
        match = re.search(r"\[RESULT\]:\s*(.*?)(?=\s*\[|\s*$)", text, re.MULTILINE | re.DOTALL)
        if match:
            result = match.group(1).strip()
            if result.lower() == "ok":
                return "OK"
            elif result.lower() == "error":
                return "ERROR"
            else:
                raise AgentInterfaceError(f"Invalid result: {result} - Expected OK or ERROR")
        logger.error("No [RESULT] found in the response", text=text)
        raise AgentInterfaceError("No [RESULT] found in the response")

    def _extract_source(self, text: str) -> str:
        """Extract the source from the text."""
        match = re.search(r"\[SOURCE\]:\s*(.*?)(?=\s*\[|\s*$)", text, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_confidence(self, result: str) -> str:
        """Extract confidence level from LLM response."""
        match = re.search(r"\[CONFIDENCE\]:\s*(.*?)(?=\s*\[|\s*$)", result, re.MULTILINE | re.DOTALL)
        if match:
            confidence = match.group(1).strip()
            if confidence.lower() == "high":
                return "HIGH"
            elif confidence.lower() == "medium":
                return "MEDIUM"
            else:
                return "LOW"
        return "LOW"

    def _is_partial(self, text: str) -> bool:
        """Check if the text is partial."""
        return "[PARTIAL]" in text

    def _detect_site_type(self, url: str) -> str | None:
        """Detect the site type from URL."""
        url_lower = url.lower()
        for site_name in self.site_selectors:
            if site_name in url_lower:
                return site_name
        return None

    async def _get_html_content(self, url: str, use_browser: bool = False) -> HTMLContent:
        """Fast exploration for extracting specific information from web pages.

        Args:
            url: The URL to explore
            use_browser: Force browser usage for JavaScript-heavy sites

        Returns:
            HTML content of the page, or "Not available" if not found
        """
        logger.debug("get_html_content called", url=url)

        # Check cache first
        cache_key = hashlib.md5(f"{url}".encode()).hexdigest()
        if cache_key in self._cache:
            logger.debug("Cache hit", url=url)
            return self._cache[cache_key]

        try:
            # Try lightweight fetch first (unless browser is required)
            if self.use_lightweight_fetch and not use_browser:
                logger.debug("Trying lightweight fetch", url=url)
                result = await self._lightweight_fetch(url)
                if result != "not found":
                    logger.debug("Lightweight fetch successful", url=url)
                    self._cache[cache_key] = result
                    return result
                logger.debug("Lightweight fetch failed, falling back to browser", url=url)

            # Fall back to browser if needed
            logger.debug("Using browser fetch", url=url)
            result = await self._browser_fetch(url)
            self._cache[cache_key] = result
            return result

        except Exception as e:
            logger.error("Failed to explore URL", url=url, error=str(e), exc_info=True)
            return "Not available"

    async def _lightweight_fetch(
        self,
        url: str,
    ) -> HTMLContent:
        """Try to fetch with simple HTTP request first."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                }
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status != 200:
                        return "not found"

                    return await response.text()

        except Exception:
            return "not found"

    async def _browser_fetch(
        self,
        url: str,
    ) -> HTMLContent:
        """Fetch with browser for JavaScript-heavy sites."""
        async with self._browser_lock:
            if self._browser is None:
                async with Stealth().use_async(async_playwright()) as p:
                    # Launch browser with English locale
                    self._browser = await p.chromium.launch(
                        headless=True, args=["--lang=en-US", "--accept-lang=en-US,en;q=0.9"]
                    )

                    # Create context with English locale and timezone
                    context = await self._browser.new_context(
                        locale="en-US",
                        timezone_id="America/New_York",
                        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                    )

                    page = await context.new_page()
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=10000)

                        # Wait a bit for dynamic content
                        await page.wait_for_timeout(1000)

                        return await page.content()

                    finally:
                        await page.close()
                        await context.close()

    async def _extract_from_html(self, html: str, site_type: str | None, url: str | None = None) -> HTMLContent:
        """Extract specific information from HTML using hybrid approach."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove excluded tags
        for tag in self.exclude_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Apply site-specific selector if available
        if site_type and site_type in self.site_selectors:
            selector = self.site_selectors[site_type]
            logger.debug("Applying site-specific selector", site_type=site_type, selector=selector)
            selected = soup.select_one(self.site_selectors[site_type])
            if selected:
                soup = selected
        elif self.css_selector:
            # Apply custom selector if provided
            logger.debug("Applying custom selector", selector=self.css_selector)
            selected = soup.select_one(self.css_selector)
            if selected:
                soup = selected

        # Initial extraction attempt
        # Get text and normalize whitespace
        raw_text = soup.get_text(separator=" ", strip=True)
        # Replace multiple spaces with single space and strip
        content = " ".join(raw_text.split())

        if not content.strip():
            logger.debug("No content found after applying selectors", url=url)
            return "No content found on page"

        logger.debug("Content extracted", content_length=len(content), content_preview=content[:200])

        return content.lower()

    async def _try_extraction(
        self,
        question: str,
        *,
        content: list[str],
        keywords: list[str] | None = None,
        parallel_number_of_chunks: int = 4,
        partial_result: str | None = None,
    ) -> str:
        """Try to extract information from content using LLM."""
        logger.debug(f"[Question]: {question}")
        logger.debug(f"[Content Size]: {len(content)}")
        logger.debug(f"[Keywords]: {keywords}")
        logger.debug(f"[Parallel Number of Chunks]: {parallel_number_of_chunks}")
        logger.debug(f"[Max Parallel Processing]: {self.max_parallel_processing}")

        # Base Case
        if not content:
            return partial_result or "Information not found"

        # If keywords are provided, we use them to filter the content that is relevant to the question

        if keywords:
            pre_filtered_content = content
            content = [c for c in content if any(keyword.lower() in c.lower() for keyword in keywords)]

            if not content:
                content = pre_filtered_content
            else:
                # Apply window reduction to focus around keywords
                content = [self._reduce_window(c, keywords) for c in content]

            logger.debug(
                "Reduced content size -> ",
                pre_filtered_content_length=len(pre_filtered_content),
                filtered_content_length=len(content),
            )

        # We define the chunks to process and remove those from the original list
        iterations = min(parallel_number_of_chunks, self.max_parallel_processing)
        logger.debug("Iterations", iterations=iterations)
        chunks_to_process = content[:iterations]
        remaining_content = content[iterations:]

        logger.debug("Chunks to process", chunks_to_process_length=len(chunks_to_process))

        # Add timing to verify parallel execution
        import time

        start_time = time.time()
        logger.info("Starting parallel processing", chunk_count=len(chunks_to_process))

        results = await asyncio.gather(*[self._process_chunk(question, content=chunk) for chunk in chunks_to_process])

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(
            "Parallel processing completed", processing_time=processing_time, chunk_count=len(chunks_to_process)
        )

        high_confidence_results = [result for result in results if self._extract_confidence(result) == "HIGH"]
        medium_confidence_results = [result for result in results if self._extract_confidence(result) == "MEDIUM"]
        low_confidence_results = [result for result in results if self._extract_confidence(result) == "LOW"]

        logger.debug(
            "results: ",
            high=len(high_confidence_results),
            medium=len(medium_confidence_results),
            low=len(low_confidence_results),
        )
        # If no high or medium confidence results and there are still chunks to process
        good_results = high_confidence_results + medium_confidence_results
        are_partial = any(self._is_partial(result) for result in good_results)

        logger.debug("Partial Results: ", are_partial=are_partial)

        if not good_results or are_partial:
            return await self._try_extraction(
                question,
                content=remaining_content,
                keywords=None,
                parallel_number_of_chunks=min(parallel_number_of_chunks + 1, self.max_parallel_processing),
                partial_result=(partial_result or "") + "\n" + "\n".join(good_results),
            )

        return "\n".join(high_confidence_results + medium_confidence_results)

    async def _process_chunk(self, question: str, *, content: str) -> str:
        """Process a single chunk of content."""
        import time

        chunk_start = time.time()

        prompt = f"Question: {question}\nContent: {content}"
        try:
            response = await self._extractor_agent.arun(prompt)
            chunk_time = time.time() - chunk_start
            logger.debug(
                "Chunk processed", processing_time=chunk_time, content_length=len(content), response=response.content
            )
            return response.content
        except Exception as e:
            chunk_time = time.time() - chunk_start
            logger.error("LLM extraction failed", error=str(e), processing_time=chunk_time, exc_info=True)
            return "Not available\n[CONFIDENCE]: LOW"

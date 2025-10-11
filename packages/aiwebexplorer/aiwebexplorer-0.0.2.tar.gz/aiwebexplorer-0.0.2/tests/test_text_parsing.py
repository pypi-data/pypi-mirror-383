"""Tests for text parsing and extraction utilities from WebExplorer class."""

import pytest

from aiwebexplorer.interfaces import AgentInterfaceError
from aiwebexplorer.webexplorer import WebExplorer


class TestTextExtraction:
    """Test text extraction utilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.webexplorer = WebExplorer()

    def test_extract_url_success(self):
        """Test successful URL extraction."""
        text = "[URL]: https://example.com\n[QUESTION]: What is this?"
        result = self.webexplorer._extract_url(text)
        assert result == "https://example.com"

    def test_extract_url_missing(self):
        """Test URL extraction when URL is missing."""
        text = "[QUESTION]: What is this?"
        with pytest.raises(AgentInterfaceError, match="No \\[URL\\] found in the response"):
            self.webexplorer._extract_url(text)

    def test_extract_url_multiple_urls(self):
        """Test URL extraction when multiple URLs are present."""
        text = "[URL]: https://first.com\n[URL]: https://second.com"
        result = self.webexplorer._extract_url(text)
        assert result == "https://first.com"

    def test_extract_question_success(self):
        """Test successful question extraction."""
        text = "[QUESTION]: What is the price of this product?"
        result = self.webexplorer._extract_question(text)
        assert result == "What is the price of this product?"

    def test_extract_question_missing(self):
        """Test question extraction when question is missing."""
        text = "[URL]: https://example.com"
        with pytest.raises(AgentInterfaceError, match="No \\[QUESTION\\] found in the response"):
            self.webexplorer._extract_question(text)

    def test_extract_question_multiline(self):
        """Test question extraction with multiline content."""
        text = """[QUESTION]: What are the main features
        of this product and its specifications?"""
        result = self.webexplorer._extract_question(text)
        assert "What are the main features" in result
        # The current regex stops at the first line break, which is expected behavior
        assert result == "What are the main features"

    def test_extract_keywords_success(self):
        """Test successful keywords extraction."""
        text = "[KEYWORDS]: price, model, specifications"
        result = self.webexplorer._extract_keywords(text)
        assert result == ["price", "model", "specifications"]

    def test_extract_keywords_empty(self):
        """Test keywords extraction when no keywords are present."""
        text = "[QUESTION]: What is this?"
        result = self.webexplorer._extract_keywords(text)
        assert result == []

    def test_extract_keywords_with_spaces(self):
        """Test keywords extraction with extra spaces."""
        text = "[KEYWORDS]: price , model , specifications "
        result = self.webexplorer._extract_keywords(text)
        assert result == ["price", "model", "specifications"]

    def test_extract_result_ok(self):
        """Test result extraction for OK status."""
        text = "[RESULT]: OK"
        result = self.webexplorer._extract_result(text)
        assert result == "OK"

    def test_extract_result_error(self):
        """Test result extraction for ERROR status."""
        text = "[RESULT]: ERROR"
        result = self.webexplorer._extract_result(text)
        assert result == "ERROR"

    def test_extract_result_invalid(self):
        """Test result extraction for invalid status."""
        text = "[RESULT]: INVALID"
        with pytest.raises(AgentInterfaceError, match="Invalid result: INVALID - Expected OK or ERROR"):
            self.webexplorer._extract_result(text)

    def test_extract_result_missing(self):
        """Test result extraction when result is missing."""
        text = "[QUESTION]: What is this?"
        with pytest.raises(AgentInterfaceError, match="No \\[RESULT\\] found in the response"):
            self.webexplorer._extract_result(text)

    def test_extract_message_success(self):
        """Test successful message extraction."""
        text = "[MESSAGE]: The question is not clear"
        result = self.webexplorer._extract_message(text)
        assert result == "The question is not clear"

    def test_extract_message_missing(self):
        """Test message extraction when message is missing."""
        text = "[RESULT]: ERROR"
        with pytest.raises(AgentInterfaceError, match="No \\[MESSAGE\\] found in the response"):
            self.webexplorer._extract_message(text)

    def test_extract_confidence_high(self):
        """Test confidence extraction for HIGH."""
        text = "[CONFIDENCE]: HIGH"
        result = self.webexplorer._extract_confidence(text)
        assert result == "HIGH"

    def test_extract_confidence_medium(self):
        """Test confidence extraction for MEDIUM."""
        text = "[CONFIDENCE]: MEDIUM"
        result = self.webexplorer._extract_confidence(text)
        assert result == "MEDIUM"

    def test_extract_confidence_low(self):
        """Test confidence extraction for LOW."""
        text = "[CONFIDENCE]: LOW"
        result = self.webexplorer._extract_confidence(text)
        assert result == "LOW"

    def test_extract_confidence_default(self):
        """Test confidence extraction default behavior."""
        text = "Some content without confidence"
        result = self.webexplorer._extract_confidence(text)
        assert result == "LOW"

    def test_extract_confidence_invalid(self):
        """Test confidence extraction for invalid value."""
        text = "[CONFIDENCE]: INVALID"
        result = self.webexplorer._extract_confidence(text)
        assert result == "LOW"

    def test_extract_source_success(self):
        """Test successful source extraction."""
        text = "[SOURCE]: Price: $299.99"
        result = self.webexplorer._extract_source(text)
        assert result == "Price: $299.99"

    def test_extract_source_missing(self):
        """Test source extraction when source is missing."""
        text = "[CONFIDENCE]: HIGH"
        result = self.webexplorer._extract_source(text)
        assert result is None

    def test_is_partial_true(self):
        """Test partial detection when [PARTIAL] is present."""
        text = "Some content [PARTIAL] more content"
        result = self.webexplorer._is_partial(text)
        assert result is True

    def test_is_partial_false(self):
        """Test partial detection when [PARTIAL] is not present."""
        text = "Some content without partial marker"
        result = self.webexplorer._is_partial(text)
        assert result is False


class TestTextProcessing:
    """Test text processing utilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.webexplorer = WebExplorer()

    def test_split_text_content_default(self):
        """Test text splitting with default parameters."""
        text = "a" * 10000  # 10k characters
        result = self.webexplorer._split_text_content(text)
        assert len(result) == 2  # Should split into 2 chunks
        assert all(len(chunk) <= 6000 for chunk in result)

    def test_split_text_content_custom_size(self):
        """Test text splitting with custom chunk size."""
        text = "a" * 1000
        result = self.webexplorer._split_text_content(text, chunk_size=500, overlap=50)
        assert len(result) == 3  # Should split into 3 chunks
        assert all(len(chunk) <= 500 for chunk in result)

    def test_split_text_content_small_text(self):
        """Test text splitting with small text."""
        text = "short text"
        result = self.webexplorer._split_text_content(text)
        assert len(result) == 1
        assert result[0] == "short text"

    def test_split_text_content_empty(self):
        """Test text splitting with empty text."""
        text = ""
        result = self.webexplorer._split_text_content(text)
        assert len(result) == 0

    def test_reduce_window_single_keyword(self):
        """Test window reduction with single keyword."""
        chunk = "This is a long text with keyword in the middle and more text after"
        keywords = ["keyword"]
        result = self.webexplorer._reduce_window(chunk, keywords, window_size=10)
        assert "keyword" in result
        assert len(result) < len(chunk)

    def test_reduce_window_multiple_keywords(self):
        """Test window reduction with multiple keywords."""
        chunk = "Text with first keyword and more text with second keyword and end"
        keywords = ["first", "second"]
        result = self.webexplorer._reduce_window(chunk, keywords, window_size=5)
        assert "first" in result
        assert "second" in result

    def test_reduce_window_no_keywords(self):
        """Test window reduction with no keywords."""
        chunk = "Some text without keywords"
        keywords = []
        result = self.webexplorer._reduce_window(chunk, keywords)
        assert result == chunk

    def test_reduce_window_keyword_not_found(self):
        """Test window reduction when keyword is not found."""
        chunk = "Some text without the keyword"
        keywords = ["missing"]
        result = self.webexplorer._reduce_window(chunk, keywords)
        assert result == chunk

    def test_reduce_window_case_insensitive(self):
        """Test window reduction with case insensitive matching."""
        chunk = "Text with KEYWORD in uppercase"
        keywords = ["keyword"]
        result = self.webexplorer._reduce_window(chunk, keywords, window_size=5)
        assert "KEYWORD" in result

    def test_reduce_window_duplicate_windows(self):
        """Test window reduction removes duplicate windows."""
        chunk = "Text with keyword and more text with keyword again"
        keywords = ["keyword"]
        result = self.webexplorer._reduce_window(chunk, keywords, window_size=10)
        # Should not contain duplicate content
        assert result.count("keyword") == 2  # Original keywords, not duplicated windows

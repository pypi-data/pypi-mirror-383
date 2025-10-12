"""Tests for site detection and HTML processing from WebExplorer class."""

import pytest

from aiwebexplorer.webexplorer import WebExplorer


class TestSiteDetection:
    """Test site detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.webexplorer = WebExplorer()

    def test_detect_site_type_amazon(self):
        """Test detecting Amazon site type."""
        url = "https://www.amazon.com/product"
        result = self.webexplorer._detect_site_type(url)
        assert result == "amazon"

    def test_detect_site_type_ebay(self):
        """Test detecting eBay site type."""
        url = "https://www.ebay.com/item"
        result = self.webexplorer._detect_site_type(url)
        assert result == "ebay"

    def test_detect_site_type_etsy(self):
        """Test detecting Etsy site type."""
        url = "https://www.etsy.com/listing"
        result = self.webexplorer._detect_site_type(url)
        assert result == "etsy"

    def test_detect_site_type_craigslist(self):
        """Test detecting Craigslist site type."""
        url = "https://craigslist.org/post"
        result = self.webexplorer._detect_site_type(url)
        assert result == "craigslist"

    def test_detect_site_type_unknown(self):
        """Test detecting unknown site type."""
        url = "https://example.com/page"
        result = self.webexplorer._detect_site_type(url)
        assert result is None

    def test_detect_site_type_case_insensitive(self):
        """Test site detection is case insensitive."""
        url = "https://www.AMAZON.com/product"
        result = self.webexplorer._detect_site_type(url)
        assert result == "amazon"

    def test_detect_site_type_subdomain(self):
        """Test site detection with subdomains."""
        url = "https://shop.amazon.com/product"
        result = self.webexplorer._detect_site_type(url)
        assert result == "amazon"

    def test_detect_site_type_custom_selectors(self):
        """Test site detection with custom selectors."""
        custom_selectors = {"custom": "div.custom-content"}
        webexplorer = WebExplorer(site_selectors=custom_selectors)

        url = "https://custom-site.com/page"
        result = webexplorer._detect_site_type(url)
        assert result == "custom"  # Should match "custom" in URL

        # Test with custom site in URL
        custom_selectors["test"] = "div.test-content"
        webexplorer = WebExplorer(site_selectors=custom_selectors)
        url = "https://test-site.com/page"
        result = webexplorer._detect_site_type(url)
        assert result == "test"


class TestHtmlProcessing:
    """Test HTML processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.webexplorer = WebExplorer()

    @pytest.mark.asyncio
    async def test_extract_from_html_basic(self):
        """Test basic HTML text extraction."""
        html = """
        <html>
            <body>
                <h1>Product Title</h1>
                <p>Product description with important details.</p>
                <div>Price: $299.99</div>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        assert "product title" in result
        assert "product description" in result
        assert "price: $299.99" in result

    @pytest.mark.asyncio
    async def test_extract_from_html_with_site_selector(self):
        """Test HTML extraction with site-specific selector."""
        html = """
        <html>
            <body>
                <div id="ppd">
                    <h1>Amazon Product</h1>
                    <p>Product details here</p>
                </div>
                <div id="other">
                    <p>This should be excluded</p>
                </div>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, "amazon")
        assert "amazon product" in result
        assert "product details here" in result
        assert "this should be excluded" not in result

    @pytest.mark.asyncio
    async def test_extract_from_html_with_custom_selector(self):
        """Test HTML extraction with custom CSS selector."""
        html = """
        <html>
            <body>
                <div class="product-info">
                    <h1>Custom Product</h1>
                    <p>Custom details</p>
                </div>
                <div class="other">
                    <p>Should be excluded</p>
                </div>
            </body>
        </html>
        """
        webexplorer = WebExplorer(css_selector=".product-info")
        result = await webexplorer._extract_from_html(html, None)
        assert "custom product" in result
        assert "custom details" in result
        assert "should be excluded" not in result

    @pytest.mark.asyncio
    async def test_extract_from_html_exclude_tags(self):
        """Test HTML extraction excludes specified tags."""
        html = """
        <html>
            <body>
                <h1>Product Title</h1>
                <script>console.log('script content');</script>
                <style>.hidden { display: none; }</style>
                <p>Visible content</p>
                <noscript>No script content</noscript>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        assert "product title" in result
        assert "visible content" in result
        assert "script content" not in result
        assert "hidden" not in result
        assert "no script content" not in result

    @pytest.mark.asyncio
    async def test_extract_from_html_empty_content(self):
        """Test HTML extraction with empty content."""
        html = """
        <html>
            <body>
                <script>console.log('only script');</script>
                <style>.hidden { display: none; }</style>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        assert result == "No content found on page"

    @pytest.mark.asyncio
    async def test_extract_from_html_whitespace_normalization(self):
        """Test HTML extraction normalizes whitespace."""
        html = """
        <html>
            <body>
                <h1>   Product    Title   </h1>
                <p>Multiple    spaces    and
                
                newlines</p>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        # Should be normalized to single spaces
        assert "product title" in result
        assert "multiple spaces and newlines" in result
        assert "   " not in result  # No multiple spaces

    @pytest.mark.asyncio
    async def test_extract_from_html_case_conversion(self):
        """Test HTML extraction converts to lowercase."""
        html = """
        <html>
            <body>
                <h1>PRODUCT TITLE</h1>
                <p>Mixed Case Content</p>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        assert result.islower()
        assert "product title" in result
        assert "mixed case content" in result

    @pytest.mark.asyncio
    async def test_extract_from_html_complex_structure(self):
        """Test HTML extraction with complex nested structure."""
        html = """
        <html>
            <head>
                <title>Page Title</title>
                <script>var data = {};</script>
            </head>
            <body>
                <header>
                    <nav>Navigation</nav>
                </header>
                <main>
                    <article>
                        <h1>Article Title</h1>
                        <section>
                            <p>Article content with <strong>important</strong> details.</p>
                            <ul>
                                <li>Feature 1</li>
                                <li>Feature 2</li>
                            </ul>
                        </section>
                    </article>
                </main>
                <footer>
                    <p>Footer content</p>
                </footer>
            </body>
        </html>
        """
        result = await self.webexplorer._extract_from_html(html, None)
        assert "article title" in result
        assert "article content with important details" in result
        assert "feature 1" in result
        assert "feature 2" in result
        assert "navigation" in result
        assert "footer content" in result
        # Script content should be excluded
        assert "var data" not in result

    @pytest.mark.asyncio
    async def test_extract_from_html_selector_not_found(self):
        """Test HTML extraction when selector doesn't match."""
        html = """
        <html>
            <body>
                <div class="other-content">
                    <p>This content should be included</p>
                </div>
            </body>
        </html>
        """
        # Try to use a selector that doesn't exist
        webexplorer = WebExplorer(css_selector=".non-existent")
        result = await webexplorer._extract_from_html(html, None)
        # Should fall back to full page content
        assert "this content should be included" in result

    @pytest.mark.asyncio
    async def test_extract_from_html_site_selector_priority(self):
        """Test that site selector takes priority over custom selector."""
        html = """
        <html>
            <body>
                <div id="ppd">
                    <h1>Amazon Product</h1>
                </div>
                <div class="custom-content">
                    <h1>Custom Product</h1>
                </div>
            </body>
        </html>
        """
        webexplorer = WebExplorer(css_selector=".custom-content")
        result = await webexplorer._extract_from_html(html, "amazon")
        # Should use Amazon selector, not custom selector
        assert "amazon product" in result
        assert "custom product" not in result

    @pytest.mark.asyncio
    async def test_extract_from_html_additional_exclude_tags(self):
        """Test HTML extraction with additional exclude tags."""
        html = """
        <html>
            <body>
                <h1>Product Title</h1>
                <video>Video content</video>
                <audio>Audio content</audio>
                <canvas>Canvas content</canvas>
                <p>Visible content</p>
            </body>
        </html>
        """
        webexplorer = WebExplorer(exclude_tags=["video", "audio"])
        result = await webexplorer._extract_from_html(html, None)
        assert "product title" in result
        assert "visible content" in result
        assert "video content" not in result
        assert "audio content" not in result
        # Canvas should still be excluded (default)
        assert "canvas content" not in result

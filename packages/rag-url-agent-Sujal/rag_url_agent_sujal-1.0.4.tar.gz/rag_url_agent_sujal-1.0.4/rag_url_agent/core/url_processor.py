import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, Tuple
import validators
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class URLProcessor:
    """Handle URL validation, expansion, and normalization."""

    # Common URL shorteners
    SHORTENERS = [
        'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
        'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'short.io'
    ]

    def __init__(self, max_redirects: int = 5, timeout: int = 10):
        self.max_redirects = max_redirects
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAGAgent/1.0)'
        })
        self._cache = {}  # Simple in-memory cache

    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url:
            return False

        # Add schema if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return validators.url(url) is True

    def normalize_url(self, url: str) -> str:
        """Normalize URL to standard format."""
        # Add schema if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Parse and reconstruct
        parsed = urlparse(url)

        # Build normalized URL
        normalized = f"{parsed.scheme}://{parsed.netloc}"

        # Add path (remove trailing slash unless it's the root)
        path = parsed.path
        if path and path != '/':
            # Remove trailing slash from non-root paths
            normalized += path.rstrip('/')
        elif not path or path == '/':
            # Don't add trailing slash for root
            pass

        # Add query if present
        if parsed.query:
            normalized += f"?{parsed.query}"

        return normalized

    def is_shortener(self, url: str) -> bool:
        """Check if URL is from a known shortener service."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix
        domain = domain.replace('www.', '')

        return any(shortener in domain for shortener in self.SHORTENERS)

    def expand_url(self, url: str) -> Tuple[str, bool]:
        """
        Expand shortened URL to final destination.
        Returns: (final_url, was_expanded)
        """
        # Check cache
        if url in self._cache:
            logger.debug(f"URL expansion cache hit for {url}")
            return self._cache[url], True

        if not self.is_shortener(url):
            return url, False

        try:
            logger.info(f"Expanding shortened URL: {url}")

            # Use HEAD request to follow redirects
            response = self.session.head(
                url,
                allow_redirects=True,
                timeout=self.timeout,
                max_redirects=self.max_redirects
            )

            final_url = response.url

            # Cache result
            self._cache[url] = final_url

            logger.info(f"Expanded to: {final_url}")
            return final_url, True

        except requests.exceptions.TooManyRedirects:
            logger.error(f"Too many redirects for URL: {url}")
            return url, False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to expand URL {url}: {e}")
            return url, False

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain."""
        return self.extract_domain(url1) == self.extract_domain(url2)

    def process_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Complete URL processing pipeline.
        Returns dict with original, normalized, and expanded URLs.
        """
        try:
            # Validate
            if not self.validate_url(url):
                logger.error(f"Invalid URL: {url}")
                return None

            # Normalize
            normalized = self.normalize_url(url)

            # Expand if shortened
            expanded, was_expanded = self.expand_url(normalized)

            result = {
                'original': url,
                'normalized': normalized,
                'final': expanded,
                'was_expanded': was_expanded,
                'domain': self.extract_domain(expanded)
            }

            logger.info(f"Processed URL: {result}")
            return result

        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return None

    def clear_cache(self):
        """Clear URL expansion cache."""
        self._cache.clear()
        logger.info("URL cache cleared")
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
from typing import Optional, Dict, Generator
import re
from urllib.parse import urljoin, urlparse
from rag_url_agent.utils.logger import get_logger
import time

logger = get_logger()

# Check if browser extractor is available
try:
    from rag_url_agent.core.browser_extractor import BrowserExtractor

    BROWSER_AVAILABLE = True
    logger.info("Browser extractor available")
except ImportError:
    BROWSER_AVAILABLE = False
    logger.warning("Browser extractor not available (install selenium)")


class ContentExtractor:
    """Extract and process content from URLs."""

    def __init__(self,
                 max_content_size: int = 10 * 1024 * 1024,  # 10MB
                 timeout: int = 30,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):

        self.max_content_size = max_content_size
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_browser_fallback = BROWSER_AVAILABLE  # MOVED HERE

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def fetch_content(self, url: str) -> Optional[bytes]:
        """Fetch raw content from URL with size limit."""
        try:
            logger.info(f"Fetching content from: {url}")

            # Stream the response to check size
            response = self.session.get(
                url,
                timeout=self.timeout,
                stream=True,
                allow_redirects=True
            )
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_size:
                logger.error(f"Content too large: {content_length} bytes")
                return None

            # Download with size limit
            content = BytesIO()
            downloaded = 0

            for chunk in response.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                if downloaded > self.max_content_size:
                    logger.error(f"Content exceeded size limit during download")
                    return None
                content.write(chunk)

            logger.info(f"Downloaded {downloaded} bytes")
            return content.getvalue()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return None

    def extract_html(self, html_content: bytes, base_url: str) -> Optional[Dict[str, str]]:
        """Extract text and metadata from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
                element.decompose()

            # Extract metadata
            title = self._extract_title(soup)
            description = self._extract_description(soup)

            # Extract main content with multiple strategies
            text = self._extract_main_content(soup)

            # If still no text, try getting all paragraph text
            if not text or len(text.strip()) < 100:
                logger.warning("Main content extraction failed, trying paragraphs")
                text = self._extract_paragraphs(soup)

            # Last resort: get all text
            if not text or len(text.strip()) < 50:
                logger.warning("Paragraph extraction failed, getting all text")
                text = soup.get_text(separator='\n', strip=True)

            # Clean text
            text = self._clean_text(text)

            # Validate we have meaningful content
            if not text or len(text.strip()) < 50:
                logger.error(f"Insufficient text content: {len(text)} characters")
                return None

            # Extract links
            links = self._extract_links(soup, base_url)

            logger.info(f"Extracted {len(text)} characters of text")

            return {
                'title': title,
                'description': description,
                'text': text,
                'links': links[:50],
                'content_type': 'html'
            }

        except Exception as e:
            logger.error(f"Failed to extract HTML content: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title with multiple fallbacks."""
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        # Try twitter:title
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        return "No title"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        return ""

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content with multiple strategies."""
        # Strategy 1: Look for article tag
        article = soup.find('article')
        if article:
            text = article.get_text(separator='\n', strip=True)
            if len(text) > 100:
                logger.info("Extracted content from <article> tag")
                return text

        # Strategy 2: Look for main tag
        main = soup.find('main')
        if main:
            text = main.get_text(separator='\n', strip=True)
            if len(text) > 100:
                logger.info("Extracted content from <main> tag")
                return text

        # Strategy 3: Look for role="main"
        role_main = soup.find(attrs={'role': 'main'})
        if role_main:
            text = role_main.get_text(separator='\n', strip=True)
            if len(text) > 100:
                logger.info("Extracted content from role='main'")
                return text

        # Strategy 4: Look for common content classes
        content_classes = [
            'article-content', 'post-content', 'entry-content', 'content',
            'article-body', 'post-body', 'story-body', 'article_body',
            'articleBody', 'post_content', 'main-content', 'page-content',
            'mw-parser-output'  # Wikipedia specific
        ]

        for class_name in content_classes:
            content = soup.find(class_=re.compile(class_name, re.I))
            if content:
                text = content.get_text(separator='\n', strip=True)
                if len(text) > 100:
                    logger.info(f"Extracted content from class: {class_name}")
                    return text

        # Strategy 5: Look for div with id containing 'content'
        content_ids = ['content', 'main', 'article', 'post', 'story', 'mw-content-text']
        for content_id in content_ids:
            content = soup.find(id=re.compile(content_id, re.I))
            if content:
                text = content.get_text(separator='\n', strip=True)
                if len(text) > 100:
                    logger.info(f"Extracted content from id: {content_id}")
                    return text

        return ""

    def _extract_paragraphs(self, soup: BeautifulSoup) -> str:
        """Extract all paragraph text."""
        paragraphs = soup.find_all('p')
        text_parts = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 20:  # Only keep substantial paragraphs
                text_parts.append(text)

        return '\n\n'.join(text_parts)

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract links from page."""
        links = []
        for link in soup.find_all('a', href=True):
            try:
                absolute_url = urljoin(base_url, link['href'])
                link_text = link.get_text(strip=True)
                if link_text and absolute_url.startswith('http'):
                    links.append({'url': absolute_url, 'text': link_text})
            except:
                continue
        return links

    def extract_pdf(self, pdf_content: bytes) -> Optional[Dict[str, str]]:
        """Extract text from PDF content."""
        try:
            logger.info("Extracting PDF content")

            pdf_file = BytesIO(pdf_content)
            pdf_reader = PdfReader(pdf_file)

            text_parts = []
            num_pages = len(pdf_reader.pages)

            # Limit pages to prevent memory issues
            max_pages = min(num_pages, 100)

            for page_num in range(max_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = '\n\n'.join(text_parts)
            full_text = self._clean_text(full_text)

            # Try to extract title from metadata
            title = ''
            if pdf_reader.metadata:
                title = pdf_reader.metadata.get('/Title', '') or pdf_reader.metadata.get('title', '')

            return {
                'title': title,
                'description': '',
                'text': full_text,
                'links': [],
                'content_type': 'pdf',
                'num_pages': num_pages
            }

        except Exception as e:
            logger.error(f"Failed to extract PDF content: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:()\-\'""\n]', '', text)

        # Remove very short lines (likely menu items, etc.)
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 3]

        return '\n'.join(cleaned_lines).strip()

    def chunk_text(self, text: str) -> Generator[Dict[str, any], None, None]:
        """Split text into overlapping chunks."""
        if not text:
            return

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = []
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Yield current chunk
                chunk_text = ' '.join(current_chunk)
                yield {
                    'text': chunk_text,
                    'index': chunk_index,
                    'word_count': current_length
                }

                # Create overlap
                overlap_words = []
                overlap_length = 0

                for sent in reversed(current_chunk):
                    sent_length = len(sent.split())
                    if overlap_length + sent_length <= self.chunk_overlap:
                        overlap_words.insert(0, sent)
                        overlap_length += sent_length
                    else:
                        break

                current_chunk = overlap_words
                current_length = overlap_length
                chunk_index += 1

            current_chunk.append(sentence)
            current_length += sentence_length

        # Yield final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            yield {
                'text': chunk_text,
                'index': chunk_index,
                'word_count': current_length
            }

    def extract_content(self, url: str) -> Optional[Dict]:
        """Main method to extract content from URL."""
        # Fetch content
        raw_content = self.fetch_content(url)
        if not raw_content:
            return None

        # Determine content type
        content_type = self._detect_content_type(url, raw_content)

        # Extract based on type
        if content_type == 'pdf':
            extracted = self.extract_pdf(raw_content)
        else:
            extracted = self.extract_html(raw_content, url)

        # If extraction failed and browser is available, try with browser
        if (not extracted or not extracted.get('text') or len(
                extracted.get('text', '')) < 100) and self.use_browser_fallback:
            logger.warning("Normal extraction failed, trying with browser...")
            try:
                from rag_url_agent.core.browser_extractor import BrowserExtractor
                browser = BrowserExtractor()
                browser_result = browser.extract_content(url)
                browser.close()

                if browser_result and browser_result.get('text'):
                    extracted = browser_result
                    extracted['description'] = ''
                    extracted['links'] = []
            except Exception as e:
                logger.error(f"Browser fallback failed: {e}")

        if not extracted or not extracted.get('text'):
            logger.error(f"No text content extracted from {url}")
            return None

        # Generate chunks
        chunks = list(self.chunk_text(extracted['text']))

        if not chunks:
            logger.error(f"No chunks generated from {url}")
            return None

        logger.info(f"Extracted {len(chunks)} chunks from {url}")

        return {
            'url': url,
            'title': extracted['title'],
            'description': extracted['description'],
            'content_type': extracted['content_type'],
            'full_text': extracted['text'],
            'chunks': chunks,
            'links': extracted.get('links', []),
            'metadata': {
                'text_length': len(extracted['text']),
                'num_chunks': len(chunks),
                'num_pages': extracted.get('num_pages')
            }
        }

    def _detect_content_type(self, url: str, content: bytes) -> str:
        """Detect content type from URL or content."""
        if url.lower().endswith('.pdf'):
            return 'pdf'
        if content.startswith(b'%PDF'):
            return 'pdf'
        return 'html'
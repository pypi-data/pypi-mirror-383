from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from typing import Optional, Dict
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class BrowserExtractor:
    """Extract content from JavaScript-heavy sites using Selenium."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Chrome driver."""
        if self.driver:
            return

        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Browser driver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def extract_content(self, url: str, wait_time: int = 5) -> Optional[Dict]:
        """Extract content from URL using browser."""
        try:
            self._init_driver()

            logger.info(f"Loading page with browser: {url}")
            self.driver.get(url)

            # Wait for page to load
            time.sleep(wait_time)

            # Get page source
            html_content = self.driver.page_source

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract title
            title = self.driver.title or "No title"

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
                element.decompose()

            # Get main content
            article = soup.find('article') or soup.find('main') or soup.find('body')
            text = article.get_text(separator='\n', strip=True) if article else ""

            logger.info(f"Extracted {len(text)} characters with browser")

            return {
                'title': title,
                'text': text,
                'content_type': 'html'
            }

        except Exception as e:
            logger.error(f"Browser extraction failed: {e}")
            return None
        finally:
            self.close()

    def close(self):
        """Close browser."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __del__(self):
        self.close()
import requests
import hashlib
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class SecurityScanner:
    """Scan URLs for security threats."""

    SCORE_SAFE = 0
    SCORE_SUSPICIOUS = 50
    SCORE_DANGEROUS = 100

    def __init__(self,
                 virustotal_api_key: Optional[str] = None,
                 google_safe_browsing_api_key: Optional[str] = None,
                 cache_duration_hours: int = 24):

        self.vt_api_key = virustotal_api_key
        self.gsb_api_key = google_safe_browsing_api_key
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._cache = {}

        # Local blacklist (can be extended)
        self.blacklist = set([
            # Add known malicious domains
        ])

        # Local whitelist (trusted domains)
        self.whitelist = set([
            'github.com', 'wikipedia.org', 'stackoverflow.com',
            'google.com', 'microsoft.com', 'python.org'
        ])

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_from_cache(self, url: str) -> Optional[Dict]:
        """Get cached security scan result."""
        cache_key = self._get_cache_key(url)

        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]

            if datetime.now() - timestamp < self.cache_duration:
                logger.debug(f"Security cache hit for {url}")
                return result
            else:
                # Expired
                del self._cache[cache_key]

        return None

    def _save_to_cache(self, url: str, result: Dict):
        """Save security scan result to cache."""
        cache_key = self._get_cache_key(url)
        self._cache[cache_key] = (result, datetime.now())

    def check_local_lists(self, url: str, domain: str) -> Dict:
        """Check URL against local blacklist/whitelist."""
        if domain in self.blacklist:
            return {
                'method': 'local_blacklist',
                'is_safe': False,
                'score': self.SCORE_DANGEROUS,
                'reason': 'Domain in local blacklist'
            }

        if domain in self.whitelist:
            return {
                'method': 'local_whitelist',
                'is_safe': True,
                'score': self.SCORE_SAFE,
                'reason': 'Domain in local whitelist'
            }

        return None

    def check_virustotal(self, url: str) -> Optional[Dict]:
        """Check URL using VirusTotal API."""
        if not self.vt_api_key:
            return None

        try:
            logger.info(f"Checking URL with VirusTotal: {url}")

            # URL scan endpoint
            headers = {'x-apikey': self.vt_api_key}

            # Get URL ID
            url_id = hashlib.sha256(url.encode()).hexdigest()

            # Check existing analysis
            response = requests.get(
                f'https://www.virustotal.com/api/v3/urls/{url_id}',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})

                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                total = sum(stats.values())

                if malicious > 0:
                    score = self.SCORE_DANGEROUS
                    is_safe = False
                elif suspicious > 2:
                    score = self.SCORE_SUSPICIOUS
                    is_safe = False
                else:
                    score = self.SCORE_SAFE
                    is_safe = True

                return {
                    'method': 'virustotal',
                    'is_safe': is_safe,
                    'score': score,
                    'malicious_count': malicious,
                    'suspicious_count': suspicious,
                    'total_scans': total
                }

            elif response.status_code == 404:
                # URL not in database, submit for scanning
                logger.info("URL not found in VirusTotal, submitting for scan")
                return self._submit_virustotal_scan(url)

        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error: {e}")

        return None

    def _submit_virustotal_scan(self, url: str) -> Dict:
        """Submit URL to VirusTotal for scanning."""
        try:
            headers = {'x-apikey': self.vt_api_key}
            data = {'url': url}

            response = requests.post(
                'https://www.virustotal.com/api/v3/urls',
                headers=headers,
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("URL submitted to VirusTotal successfully")
                return {
                    'method': 'virustotal',
                    'is_safe': True,  # Assume safe until scanned
                    'score': self.SCORE_SAFE,
                    'status': 'pending_scan'
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal submission error: {e}")

        return None

    def check_google_safe_browsing(self, url: str) -> Optional[Dict]:
        """Check URL using Google Safe Browsing API."""
        if not self.gsb_api_key:
            return None

        try:
            logger.info(f"Checking URL with Google Safe Browsing: {url}")

            api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.gsb_api_key}'

            payload = {
                'client': {
                    'clientId': 'rag-agent',
                    'clientVersion': '1.0.0'
                },
                'threatInfo': {
                    'threatTypes': [
                        'MALWARE',
                        'SOCIAL_ENGINEERING',
                        'UNWANTED_SOFTWARE',
                        'POTENTIALLY_HARMFUL_APPLICATION'
                    ],
                    'platformTypes': ['ANY_PLATFORM'],
                    'threatEntryTypes': ['URL'],
                    'threatEntries': [{'url': url}]
                }
            }

            response = requests.post(api_url, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if 'matches' in data and len(data['matches']) > 0:
                    threat_type = data['matches'][0].get('threatType', 'UNKNOWN')
                    return {
                        'method': 'google_safe_browsing',
                        'is_safe': False,
                        'score': self.SCORE_DANGEROUS,
                        'threat_type': threat_type
                    }
                else:
                    return {
                        'method': 'google_safe_browsing',
                        'is_safe': True,
                        'score': self.SCORE_SAFE,
                        'threat_type': None
                    }

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Safe Browsing API error: {e}")

        return None

    def scan_url(self, url: str, domain: str) -> Dict:
        """
        Comprehensive URL security scan.
        Returns security assessment with score.
        """
        # Check cache first
        cached = self._get_from_cache(url)
        if cached:
            return cached

        results = []

        # Check local lists
        local_check = self.check_local_lists(url, domain)
        if local_check:
            results.append(local_check)

            # If blacklisted, return immediately
            if not local_check['is_safe']:
                self._save_to_cache(url, local_check)
                return local_check

        # Check VirusTotal
        vt_result = self.check_virustotal(url)
        if vt_result:
            results.append(vt_result)

        # Check Google Safe Browsing
        gsb_result = self.check_google_safe_browsing(url)
        if gsb_result:
            results.append(gsb_result)

        # Aggregate results
        if not results:
            final_result = {
                'methods': ['none'],
                'is_safe': True,
                'score': self.SCORE_SAFE,
                'reason': 'No security checks available',
                'details': []
            }
        else:
            # Calculate aggregate score
            max_score = max(r['score'] for r in results)
            is_safe = all(r['is_safe'] for r in results)

            final_result = {
                'methods': [r['method'] for r in results],
                'is_safe': is_safe,
                'score': max_score,
                'details': results
            }

        # Cache result
        self._save_to_cache(url, final_result)

        logger.info(f"Security scan complete for {url}: Score={final_result['score']}, Safe={final_result['is_safe']}")

        return final_result

    def add_to_blacklist(self, domain: str):
        """Add domain to local blacklist."""
        self.blacklist.add(domain)
        logger.info(f"Added {domain} to blacklist")

    def add_to_whitelist(self, domain: str):
        """Add domain to local whitelist."""
        self.whitelist.add(domain)
        logger.info(f"Added {domain} to whitelist")

    def clear_cache(self):
        """Clear security scan cache."""
        self._cache.clear()
        logger.info("Security cache cleared")
# Security Scanner

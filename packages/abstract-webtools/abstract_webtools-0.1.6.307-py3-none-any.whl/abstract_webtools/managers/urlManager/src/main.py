import logging
import requests
from .functions.url_utils import parse_url, dictquery, reconstructUrlParse, reconstructNetLoc
from .functions.domain_utils import get_extention, domain_exists
from .functions.specUrl_utils import get_corrected_url, reconstructUrlFromUrlParse
from .imports.constants import ALL_URL_KEYS

logging.basicConfig(level=logging.INFO)

class urlManager:
    """
    urlManager for managing and cleaning URLs.

    Uses shared functions from domain_utils/url_utils/specUrl_utils.
    """

    def __init__(self, url=None, session=None):
        self.session = session or requests.Session()
        self._url = url
        self.parsed = None

        if url is None:
            self.url = None
            self.clean_urls = []
            self.protocol = None
            self.domain = None
            self.path = ""
            self.query = {}
            self.all_urls = []
        else:
            self.update_url(url)

    def update_url(self, url):
        """Update the URL and refresh related attributes."""
        self._url = url
        if url is None:
            self.clean_urls = []
            self.url = None
            self.protocol = None
            self.domain = None
            self.path = ""
            self.query = {}
            self.all_urls = []
            return

        # Parse + normalize
        self.parsed = parse_url(url)
        self.clean_urls = self._generate_variants(self.parsed)
        self.url = self.get_correct_url() or reconstructUrlFromUrlParse(parsed=self.parsed)
        self.protocol = self.parsed.get("scheme")
        self.domain = reconstructNetLoc(self.parsed.get("netloc"))
        self.path = self.parsed.get("path")
        self.query = self.parsed.get("query")
        self.all_urls = self.clean_urls

    def _generate_variants(self, parsed) -> list:
        """Generate candidate URLs using ALL_URL_KEYS (scheme, www, extensions)."""
        netloc_data = parsed.get("netloc", {})
        base_domain = netloc_data.get("domain", "")
        ext = netloc_data.get("extention", "")
        variants = []

        for scheme in ALL_URL_KEYS["scheme"]:
            for www in ALL_URL_KEYS["netloc"]["www"]:
                for ext_cand in (ALL_URL_KEYS["netloc"]["extentions"][0] + ALL_URL_KEYS["netloc"]["extentions"][1]):
                    # skip if extension already fixed and doesn't match
                    if ext and ext != ext_cand:
                        continue
                    candidate_netloc = f"{'www.' if www else ''}{base_domain}{ext_cand or ext}"
                    candidate_url = f"{scheme}://{candidate_netloc}{parsed.get('path','')}"
                    variants.append(candidate_url)

        # Deduplicate
        seen = set()
        unique_variants = [v for v in variants if not (v in seen or seen.add(v))]
        return sorted(unique_variants, key=lambda v: (not v.startswith("https"), v))

    def get_correct_url(self, candidates=None) -> str:
        """
        Try candidates (HEAD request). 
        Return first that resolves with 200.
        """
        candidates = candidates or self.clean_urls
        for candidate in candidates:
            try:
                response = self.session.head(candidate, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return candidate
            except requests.exceptions.RequestException as e:
                logging.info(f"Failed: {candidate} ({e})")
        return None

    # === convenience wrappers ===
    def get_domain(self) -> str:
        if not self.parsed:
            return None
        return reconstructNetLoc(self.parsed.get("netloc"))

    def is_valid_url(self, url=None):
        """Check if a URL parses into scheme+netloc."""
        url = url or self.url
        if not url:
            return False
        p = parse_url(url)
        return bool(p.get("scheme")) and bool(p.get("netloc", {}).get("domain"))

    def make_valid(self, href, base_url=None):
        """
        Fix relative links by joining with a base URL.
        If base_url is not provided, uses self.url.
        """
        base_url = base_url or self.url
        if not base_url:
            return None
        return requests.compat.urljoin(base_url, href)


    def base_url(self):
        """Return base of current url (scheme+domain)."""
        if not self.parsed:
            return None
        scheme = self.parsed.get("scheme")
        netloc = reconstructNetLoc(self.parsed.get("netloc"))
        return f"{scheme}://{netloc}/"

    def url_basename(self):
        if not self.parsed:
            return ""
        return self.parsed.get("path", "").strip("/").split("/")[-1]

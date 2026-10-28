"""
PaperLensAI – PubMed API Service
Fetches real medical abstracts from NCBI PubMed E-utilities
"""
import os
import logging
import httpx
from typing import List, Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_SEARCH = f"{PUBMED_BASE}/esearch.fcgi"
PUBMED_FETCH = f"{PUBMED_BASE}/efetch.fcgi"
PUBMED_SUMMARY = f"{PUBMED_BASE}/esummary.fcgi"


class PubMedService:
    def __init__(self):
        self.api_key = os.getenv("PUBMED_API_KEY", "")
        self.timeout = 30.0

    @property
    def is_connected(self) -> bool:
        return True  # PubMed is a free public API

    def _base_params(self) -> dict:
        params = {"db": "pubmed", "retmode": "xml"}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    async def search_abstracts(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[dict]:
        """
        Search PubMed and fetch full abstracts for the given query.
        Returns a list of article dicts.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Step 1: Search for PMIDs
            search_params = {
                **self._base_params(),
                "term": query + "[Title/Abstract]",
                "retmax": max_results,
                "usehistory": "y",
                "sort": "relevance",
            }
            try:
                search_resp = await client.get(PUBMED_SEARCH, params=search_params)
                search_resp.raise_for_status()
                search_tree = ET.fromstring(search_resp.text)
                pmids = [id_elem.text for id_elem in search_tree.findall(".//Id")]

                if not pmids:
                    logger.info(f"No PubMed results for query: {query}")
                    return []

                # Step 2: Fetch full records
                fetch_params = {
                    **self._base_params(),
                    "id": ",".join(pmids),
                    "rettype": "abstract",
                }
                fetch_resp = await client.get(PUBMED_FETCH, params=fetch_params)
                fetch_resp.raise_for_status()

                articles = self._parse_articles(fetch_resp.text, pmids)
                return articles

            except httpx.TimeoutException:
                logger.error("PubMed API timeout")
                return []
            except Exception as e:
                logger.error(f"PubMed API error: {e}")
                return []

    def _parse_articles(self, xml_text: str, pmids: List[str]) -> List[dict]:
        """Parse PubMed XML response into article dicts."""
        articles = []
        try:
            root = ET.fromstring(xml_text)
            for article_elem in root.findall(".//PubmedArticle"):
                try:
                    art = self._extract_article(article_elem)
                    if art and art.get("abstract"):
                        articles.append(art)
                except Exception as e:
                    logger.warning(f"Failed to parse article: {e}")
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
        return articles

    def _extract_article(self, elem) -> Optional[dict]:
        """Extract fields from a PubmedArticle XML element."""
        # PMID
        pmid_elem = elem.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else "unknown"

        # Title
        title_elem = elem.find(".//ArticleTitle")
        title = self._clean_text(title_elem.text if title_elem is not None else "")

        # Abstract
        abstract_parts = elem.findall(".//AbstractText")
        abstract = " ".join(
            self._clean_text(p.text or "") for p in abstract_parts
            if p.text
        )

        if not abstract:
            return None  # Skip articles without abstracts

        # Authors
        authors = []
        for author in elem.findall(".//Author"):
            last = author.findtext("LastName", "")
            first = author.findtext("ForeName", "")
            if last:
                authors.append(f"{last} {first}".strip())
        authors_str = ", ".join(authors[:5])
        if len(authors) > 5:
            authors_str += f" et al."

        # Date
        pub_date = elem.find(".//PubDate")
        year = pub_date.findtext("Year", "") if pub_date is not None else ""
        month = pub_date.findtext("Month", "") if pub_date is not None else ""
        pub_date_str = f"{month} {year}".strip() if year else "Unknown"

        # Journal
        journal_elem = elem.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else ""

        # DOI
        doi = ""
        for id_elem in elem.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                doi = id_elem.text or ""
                break

        return {
            "pmid": pmid,
            "title": title,
            "authors": authors,
            "authors_str": authors_str,
            "abstract": abstract,
            "publication_date": pub_date_str,
            "journal": journal,
            "doi": doi,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        }

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove XML tags and excessive whitespace
        import re
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# Singleton
pubmed_service = PubMedService()

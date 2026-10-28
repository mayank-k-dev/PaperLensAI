"""
PaperLensAI – PubMed Router
Search and auto-summarize from PubMed
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from models.schemas import PubMedSearchRequest, PubMedSearchResponse, PubMedArticle
from services.pubmed_service import pubmed_service
from services.gemini_service import gemini_service
from services.quality_scorer import quality_scorer
from routers.summarize import build_summary_response
import uuid

router = APIRouter(prefix="/api/pubmed", tags=["pubmed"])
logger = logging.getLogger(__name__)


@router.post("/search", response_model=PubMedSearchResponse)
async def search_pubmed(request: PubMedSearchRequest):
    """
    Search PubMed for medical literature and optionally auto-summarize results.
    """
    logger.info(f"PubMed search: '{request.query}' (max={request.max_results})")

    articles_raw = await pubmed_service.search_abstracts(
        query=request.query,
        max_results=request.max_results,
    )

    if not articles_raw:
        raise HTTPException(
            status_code=404,
            detail=f"No abstracts found on PubMed for query: '{request.query}'. Try different keywords."
        )

    # Build PubMedArticle models
    articles = [
        PubMedArticle(
            pmid=a["pmid"],
            title=a["title"],
            authors=a["authors"],
            abstract=a["abstract"],
            publication_date=a["publication_date"],
            journal=a.get("journal", ""),
            doi=a.get("doi", ""),
            pubmed_url=a["pubmed_url"],
        )
        for a in articles_raw
    ]

    summaries = None
    if request.summarize:
        summaries = []
        for a in articles_raw:
            try:
                ai_result = await gemini_service.summarize_abstract(
                    abstract=a["abstract"],
                    title=a["title"],
                    authors=a["authors_str"],
                    depth=request.depth.value,
                )
                summary = build_summary_response(
                    request_id=str(uuid.uuid4()),
                    abstract=a["abstract"],
                    title=a["title"],
                    authors=a["authors_str"],
                    pub_date=a["publication_date"],
                    ai_result=ai_result,
                )
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to summarize PMID {a['pmid']}: {e}")

    return PubMedSearchResponse(
        query=request.query,
        total_found=len(articles),
        articles=articles,
        summaries=summaries,
    )


@router.get("/article/{pmid}")
async def get_article_by_pmid(pmid: str):
    """Fetch a specific PubMed article by PMID."""
    articles = await pubmed_service.search_abstracts(
        query=f"{pmid}[uid]",
        max_results=1,
    )
    if not articles:
        raise HTTPException(status_code=404, detail=f"Article {pmid} not found")
    return articles[0]

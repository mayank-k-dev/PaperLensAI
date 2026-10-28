"""
PaperLensAI – Pydantic schemas for request/response models
Medical Literature Summarization with Multi-Dimensional Analysis
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SummaryDepth(str, Enum):
    brief = "brief"
    standard = "standard"
    detailed = "detailed"


class AbstractRequest(BaseModel):
    abstract: str = Field(..., min_length=50, description="Medical abstract text to summarize")
    title: Optional[str] = Field(None, description="Paper title (optional)")
    authors: Optional[str] = Field(None, description="Author list (optional)")
    publication_date: Optional[str] = Field(None, description="Publication date")
    depth: SummaryDepth = Field(SummaryDepth.standard, description="Summary depth level")
    highlight_clinical: bool = Field(True, description="Highlight clinical relevance")
    gemini_api_key: Optional[str] = Field(None, description="Optional custom Gemini API key")


class BatchAbstractItem(BaseModel):
    id: str
    abstract: str
    title: Optional[str] = None
    authors: Optional[str] = None
    publication_date: Optional[str] = None


class BatchRequest(BaseModel):
    abstracts: List[BatchAbstractItem]
    depth: SummaryDepth = SummaryDepth.standard
    gemini_api_key: Optional[str] = None


class KeyFinding(BaseModel):
    finding: str
    importance: str  # high / medium / low
    category: str   # methodology / result / conclusion / limitation
    metric_value: Optional[str] = None


class QualityMetrics(BaseModel):
    overall_score: float
    readability_score: float
    completeness_score: float
    accuracy_indicator: float
    coherence_score: float
    rouge_l_approx: Optional[float] = 88.5
    clinical_relevance_score: Optional[float] = 92.0
    grade: str  # A+ / A / B


class PicoFramework(BaseModel):
    population: str
    intervention: str
    comparator: str
    outcome: str


class NumericalMetrics(BaseModel):
    sample_size_n: Optional[str] = None
    primary_hazard_ratio: Optional[str] = None
    confidence_interval: Optional[str] = None
    p_value: Optional[str] = None
    relative_risk_reduction: Optional[str] = None
    nnt: Optional[str] = None
    adverse_event_rate: Optional[str] = None


class ForestPlotData(BaseModel):
    label: str
    effect_size: float
    ci_lower: float
    ci_upper: float
    favored_arm: str
    is_significant: bool


class TheoreticalAnalysis(BaseModel):
    pico: Optional[PicoFramework] = None
    evidence_level: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    risk_of_bias: Optional[str] = None
    guideline_impact: Optional[str] = None


class SummaryResponse(BaseModel):
    id: str
    title: Optional[str]
    authors: Optional[str]
    publication_date: Optional[str]
    summary: str
    key_findings: List[KeyFinding]
    clinical_relevance: Optional[str]
    methodology_type: Optional[str]
    keywords: List[str]
    limitations: Optional[str]
    quality: QualityMetrics
    processing_time_ms: float
    # Enhanced theoretical, numerical and graphical payload
    theoretical: Optional[TheoreticalAnalysis] = None
    numerical: Optional[NumericalMetrics] = None
    forest_plot: Optional[ForestPlotData] = None


class BatchSummaryResponse(BaseModel):
    total: int
    processed: int
    failed: int
    results: List[SummaryResponse]
    avg_quality_score: float
    cross_study_synthesis: Optional[str] = None


class PubMedSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search query for PubMed")
    max_results: int = Field(5, ge=1, le=20, description="Max number of results")
    summarize: bool = Field(True, description="Auto-summarize fetched abstracts")
    depth: SummaryDepth = SummaryDepth.standard
    gemini_api_key: Optional[str] = None


class PubMedArticle(BaseModel):
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    journal: Optional[str]
    doi: Optional[str]
    pubmed_url: str


class PubMedSearchResponse(BaseModel):
    query: str
    total_found: int
    articles: List[PubMedArticle]
    summaries: Optional[List[SummaryResponse]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    gemini_connected: bool
    pubmed_connected: bool

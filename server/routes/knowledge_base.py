from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from server.db.store import store
from server.models.schemas import KnowledgeArticle

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.get("", response_model=List[KnowledgeArticle])
async def list_knowledge_articles(
    query: Optional[str] = Query(None, description="Search by keywords, symptoms, or tags"),
    product_area: Optional[str] = Query(None, description="Filter by product area"),
    tag: Optional[str] = Query(None, description="Filter by specific tag"),
):
    """Search and filter internal knowledge-base articles and runbooks."""
    return store.list_knowledge_articles(query=query, product_area=product_area, tag=tag)


@router.get("/{article_id}", response_model=KnowledgeArticle)
async def get_knowledge_article(article_id: str):
    """Retrieve full article content and diagnostic steps."""
    article = store.get_knowledge_article(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge article '{article_id}' not found",
        )
    return article

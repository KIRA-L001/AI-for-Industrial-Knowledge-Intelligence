"""Aggregates all v1 API routers into a single router mounted by the app.

Feature routers are added here as each phase lands (auth, projects, documents,
search, chat, ...). Keeping a single aggregation point keeps `main.py` thin.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    analytics,
    auth,
    chat,
    documents,
    equipment,
    graph,
    health,
    knowledge,
    plants,
    projects,
    reports,
    retrieval,
    search,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(plants.router)
api_router.include_router(projects.router)
api_router.include_router(equipment.router)
api_router.include_router(documents.router)
api_router.include_router(knowledge.router)
api_router.include_router(graph.router)
api_router.include_router(search.router)
api_router.include_router(retrieval.router)
api_router.include_router(chat.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)

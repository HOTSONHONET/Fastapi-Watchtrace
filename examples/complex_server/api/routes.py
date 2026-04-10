from fastapi import APIRouter, Query
from ..services.profile_service import build_user_dashboard

router = APIRouter()

@router.get("/dashboard/{user_id}")
def get_dashboard(
    user_id: int,
    include_recommendations: bool = Query(True),
    include_analytics: bool = Query(True),
):
    return build_user_dashboard(
        user_id=user_id,
        include_recommendations=include_recommendations,
        include_analytics=include_analytics,
    )
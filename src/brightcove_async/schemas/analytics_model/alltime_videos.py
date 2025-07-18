from pydantic import BaseModel


class AllTimeVideoAnalyticsResponse(BaseModel):
    alltime_video_views: int = 0

# news/urls.py
from django.urls import path
from .views import (
    get_news_view,
    get_sources_view,
    get_random_view,
    get_section_view,
    stats_view,
)

urlpatterns = [
    path("", get_news_view, name="news-list"),                          # /news/?q=Deportes&limit=50
    path("sources/", get_sources_view, name="news-sources"),            # /news/sources/
    path("random/", get_random_view, name="news-random"),               # /news/random/?limit=10
    path("section/<slug:section>/", get_section_view, name="news-section"),  # /news/section/tecnologia/
    path("stats/", stats_view, name="news-stats"),                      # /news/stats/
]

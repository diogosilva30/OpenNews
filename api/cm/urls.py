from django.urls import path

from .views import CMURLSearchView, CMKeywordSearchView, CMTagSearchView


urlpatterns = [
    path(
        "url_search/",
        CMURLSearchView.as_view(),
        name="cm_url_search",
    ),
    path(
        "tag_search/",
        CMTagSearchView.as_view(),
        name="cm_tag_search",
    ),
    path(
        "keyword_search/",
        CMKeywordSearchView.as_view(),
        name="cm_keyword_search",
    ),
]

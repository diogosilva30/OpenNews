from django.urls import path

from .views import PublicoURLSearchView, PublicoTagSearchView, PublicoKeywordSearchView


urlpatterns = [
    path(
        "url_search/",
        PublicoURLSearchView.as_view(),
        name="publico_url_search",
    ),
    path(
        "tag_search/",
        PublicoTagSearchView.as_view(),
        name="publico_tag_search",
    ),
    path(
        "keyword_search/",
        PublicoKeywordSearchView.as_view(),
        name="publico_keyword_search",
    ),
]

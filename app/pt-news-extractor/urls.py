"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/

"""
from django.contrib import admin
from django.urls import path, include


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="PT NEWS EXTRACTOR API",
        default_version="v2",
        description="PT-NEWS-EXTRACTOR is a REST API made in Python to extract news from Portuguese journals. It is intended for academic use.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="diogosilv30@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path(
        "",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("admin/", admin.site.urls),
    path(
        "api-auth/",
        include(
            "rest_framework.urls",
            namespace="rest",
        ),
    ),
    path("django-rq/", include("django_rq.urls")),
    path("api/publico/", include("publico.urls")),
    path("api/cm/", include("cm.urls")),
    path("api/results/", include("results.urls")),
]

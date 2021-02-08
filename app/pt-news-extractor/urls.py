"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/

"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
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

"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/

"""
from django.urls import path, include


from drf_spectacular.views import SpectacularRedocView, SpectacularAPIView


urlpatterns = [
    path("", SpectacularRedocView.as_view(), name="redoc"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("publico/", include("publico.urls")),
    path("cm/", include("cm.urls")),
    path("results/", include("results.urls")),
]

"""
Contains the Django URLs for the 'results' app
"""

from django.urls import path

from .views import ResultsView


urlpatterns = [
    path("<str:job_id>/", ResultsView.as_view(), name="results"),
]

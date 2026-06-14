from django.urls import path

from apps.story.views import (
    ExportDownloadView,
    ExportSummaryView,
    ExportValidateView,
    JobItemView,
    JobListView,
    JobRetryView,
    ProjectCollectionView,
    ProjectItemView,
    ShotItemView,
    ShotListView,
)

urlpatterns = [
    path("projects/", ProjectCollectionView.as_view(), name="story-projects"),
    path("projects/<int:project_id>/", ProjectItemView.as_view(), name="story-project-detail"),
    path("projects/<int:project_id>/shots/", ShotListView.as_view(), name="story-shots"),
    path("shots/<int:shot_id>/", ShotItemView.as_view(), name="story-shot-detail"),
    path("projects/<int:project_id>/jobs/", JobListView.as_view(), name="story-jobs"),
    path("jobs/<int:job_id>/", JobItemView.as_view(), name="story-job-detail"),
    path("jobs/<int:job_id>/retry/", JobRetryView.as_view(), name="story-job-retry"),
    path("projects/<int:project_id>/export-summary/", ExportSummaryView.as_view(), name="story-export-summary"),
    path("projects/<int:project_id>/export-validate/", ExportValidateView.as_view(), name="story-export-validate"),
    path("projects/<int:project_id>/export-download/", ExportDownloadView.as_view(), name="story-export-download"),
]

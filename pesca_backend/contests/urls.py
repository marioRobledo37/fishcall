from django.urls import path
from . import views
from .views import capture_sync

urlpatterns = [
    
    path("api/capture/", capture_sync),

    path(
        "contest/<int:contest_id>/live/",
        views.live_board,
        name="live_board"
    ),
    
    path(
        "contest/<int:contest_id>/broadcast/",
        views.broadcast_view,
        name="broadcast_view"
    ),

    path(
        "contest/<int:contest_id>/director/",
        views.director_panel,
        name="director_panel"
    ),

    path(
        "fiscal/capture/",
        views.fiscal_capture,
        name="fiscal_capture"
    ),

    path(
        "save_subscription/",
        views.save_subscription,
        name="save_subscription"
    ),
    
    path(
        "contest/<int:contest_id>/captures-json/",
        views.live_captures_json,
        name="live_captures_json"
    ),

]
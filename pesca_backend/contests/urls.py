from django.urls import path
from . import views

urlpatterns = [

    path(
        "contest/<int:contest_id>/live/",
        views.live_board,
        name="live_board"
    ),

    path(
        "contest/<int:contest_id>/broadcast/",
        views.broadcast_view,
        name="broadcast"
    ),

    path(
        "contest/<int:contest_id>/captures-json/",
        views.captures_json,
        name="captures_json"
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
        "api/capture/",
        views.capture_sync
    ),

    path(
        "save_subscription/",
        views.save_subscription
    ),

]
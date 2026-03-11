from django.urls import path
from . import views

urlpatterns = [

path("contest/<int:contest_id>/live/",views.live_board),

path("contest/<int:contest_id>/broadcast/",views.broadcast_view),

path("contest/<int:contest_id>/captures-json/",views.captures_json),

path("contest/<int:contest_id>/ranking/",views.ranking_board),

path("director/<int:contest_id>/",views.director_panel),

path("fiscal/",views.fiscal_capture),

path("api/capture-sync/",views.capture_sync),

path("api/save-subscription/",views.save_subscription),

path(
"contest/<int:contest_id>/pending/",
views.pending_captures
),

path(
"capture/<int:capture_id>/approve/",
views.approve_capture
),

path(
    "capture/<int:capture_id>/reject/",
    views.reject_capture
),

path(
    "contest/<int:contest_id>/pay/<int:fisher_id>/",
    views.pay_registration,
    name="pay_registration"
),

path(
    "join/<str:code>/",
    views.join_contest,
    name="join_contest"
),

path(
    "join/<str:code>/register/",
    views.register_contest,
    name="register_contest"
),

path(
    "api/fisher-lookup/",
    views.fisher_lookup_dni,
    name="fisher_lookup_dni"
)

]
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

]
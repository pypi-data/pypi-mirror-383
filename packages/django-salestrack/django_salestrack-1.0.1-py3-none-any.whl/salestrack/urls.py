from django.urls import path
from .views import user_day_track, get_user_markers, track_map_page


app_name = 'salestrack'


urlpatterns = [
    path('tracks.geo/', user_day_track, name='user_day_track'),
    path('user-markers/', get_user_markers, name='get_user_markers'),
    path('', track_map_page, name='track_map_page'),
]
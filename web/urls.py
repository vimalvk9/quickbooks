"""
Contians URL patterns for web app
"""

from django.conf.urls import url
from django.urls import path
from .views import user_list_view
from .views import user_detail_update_delete_view
from .views import index


urlpatterns = [

    path("user/", user_list_view, name="home"),
    path("user/<int:id>/", user_detail_update_delete_view, name="home"),
    path("accounts/<int:id>/", user_detail_update_delete_view, name="home"),
    path("apiKey/", user_detail_update_delete_view, name="home"),
    url(r'^(?P<path>.*)$', index, name="index"),
]


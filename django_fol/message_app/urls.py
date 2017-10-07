# message_app/urls.py
from django.conf.urls import url

from .views import Home_page_view

urlpatterns = [
    url(r'^$', Home_page_view.as_view()),
]

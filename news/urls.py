from django.urls import path

from . import views

urlpatterns = [
    path("count/", views.count, name="count"),
    path("case/", views.case, name="case"),
    path("graph/", views.graph, name="graph"),
    path("newslist/", views.newslist, name="newslist"),
    path("press/", views.press, name="press"),
]

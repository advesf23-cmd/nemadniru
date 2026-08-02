from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("<str:slug>/comment/", views.AddCommentView.as_view(), name="add_comment"),
    path("<str:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]

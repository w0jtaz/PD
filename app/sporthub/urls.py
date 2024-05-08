from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    path('login', views.home, name="sporthub-home"),
    path('about/', views.about, name="sporthub-about"),

    path('', PostListView.as_view(), name="sporthub-home"),
    path('post-new/', PostCreateView.as_view(), name="sporthub-new"),
    path('post/<int:pk>/', PostDetailView.as_view(), name="sporthub-detail"),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name="sporthub-update"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="sporthub-delete")
]

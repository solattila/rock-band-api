from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rockband import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('members', views.MemberViewSet)

app_name = 'rockband'

urlpatterns = [
    path('', include(router.urls))
]

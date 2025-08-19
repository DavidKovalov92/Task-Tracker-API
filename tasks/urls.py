from .views import TeamViewSet, TaskViewSet, GetUserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', GetUserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'team', TeamViewSet, basename='team')


urlpatterns = [] + router.urls
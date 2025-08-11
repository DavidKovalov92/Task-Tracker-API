from .views import TeamViewSet, TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'team', TeamViewSet, basename='team')


urlpatterns = [] + router.urls
from .views import TeamViewSet, TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'team', TeamViewSet, basename='user')
router.register(r'task', TaskViewSet, basename='user')

urlpatterns = router.urls + []
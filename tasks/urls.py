from .views import TeamViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'team', TeamViewSet, basename='user')

urlpatterns = router.urls + []
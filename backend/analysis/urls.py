from rest_framework.routers import DefaultRouter
from .views import InsightViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'insights', InsightViewSet, basename='insight')
router.register(r'chats', ChatMessageViewSet, basename='chat')

urlpatterns = router.urls
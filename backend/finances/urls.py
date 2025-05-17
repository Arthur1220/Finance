from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, GoalViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = router.urls
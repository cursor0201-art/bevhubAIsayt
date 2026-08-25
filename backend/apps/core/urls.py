from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from core.views.project_views import ProjectViewSet
from core.views.auth_views import UserRegistrationView, CustomTokenObtainPairView, UserProfileView, ChangePasswordView, DeleteAccountView
from core.views.billing_views import BillingDashboardView, SubscribePlanView, ApplyPromoCodeView
from core.views.preferences_views import AIPreferencesView
from core.views.workspace_views import (
    WorkspaceViewSet, 
    AITaskViewSet, 
    ProjectFileViewSet, 
    IntegrationViewSet, 
    DeploymentViewSet, 
    TemplateListView, 
    UserJourneyHistoryView
)
from core.views.analytics_views import (
    RevenueDashboardView, 
    AIQualityDashboardView, 
    UserJourneyTelemetryView, 
    ProductIntelligenceDashboardView,
    TelemetryDrilldownView
)

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('workspaces', WorkspaceViewSet, basename='workspace')
router.register('ai-tasks', AITaskViewSet, basename='ai_tasks')
router.register('files', ProjectFileViewSet, basename='files')
router.register('integrations', IntegrationViewSet, basename='integrations')
router.register('deployments', DeploymentViewSet, basename='deployments')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    
    # Templates & History
    path('templates/', TemplateListView.as_view(), name='templates_list'),
    path('analytics/history/', UserJourneyHistoryView.as_view(), name='user_journey_history'),
    
    # Billing & Monetization routes
    path('billing/dashboard/', BillingDashboardView.as_view(), name='billing_dashboard'),
    path('billing/subscribe/', SubscribePlanView.as_view(), name='billing_subscribe'),
    path('billing/promo/', ApplyPromoCodeView.as_view(), name='billing_promo'),

    # Analytics & Quality routes
    path('analytics/revenue/', RevenueDashboardView.as_view(), name='analytics_revenue'),
    path('analytics/quality/', AIQualityDashboardView.as_view(), name='analytics_quality'),
    path('analytics/telemetry/', UserJourneyTelemetryView.as_view(), name='analytics_telemetry'),
    path('analytics/product-intelligence/', ProductIntelligenceDashboardView.as_view(), name='analytics_product_intelligence'),
    path('analytics/product-intelligence/drilldown/', TelemetryDrilldownView.as_view(), name='analytics_product_intelligence_drilldown'),

    # Preferences & Customizations
    path('ai/preferences/', AIPreferencesView.as_view(), name='ai_preferences'),
]





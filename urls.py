from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, MeView, my_profile, PublicCoachViewSet, PublicPlanViewSet,
    ProgramViewSet, NutritionViewSet, AdminCoachViewSet, PlanViewSet,
    UserAdminViewSet, OrderViewSet, CoachRequestViewSet, AdminSettingsViewSet,
    CoachingSessionViewSet, PrivateCoachReviewViewSet, public_payment_settings,
    approve_order, reject_order, admin_overview, public_site_content, submit_manual_payment, admin_account
)

router = DefaultRouter()
router.register("public/coaches", PublicCoachViewSet, basename="public-coaches")
router.register("public/plans", PublicPlanViewSet, basename="public-plans")
router.register("admin/users", UserAdminViewSet, basename="admin-users")
router.register("admin/coaches", AdminCoachViewSet, basename="admin-coaches")
router.register("admin/plans", PlanViewSet, basename="admin-plans")
router.register("admin/programs", ProgramViewSet, basename="admin-programs")
router.register("admin/nutrition", NutritionViewSet, basename="admin-nutrition")
router.register("admin/settings", AdminSettingsViewSet, basename="admin-settings")
router.register("orders", OrderViewSet, basename="orders")
router.register("coach-requests", CoachRequestViewSet, basename="coach-requests")
router.register("sessions", CoachingSessionViewSet, basename="sessions")
router.register("private/coach-reviews", PrivateCoachReviewViewSet, basename="private-coach-reviews")

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),
    path("me/profile/", my_profile),
    path("public/payment-settings/", public_payment_settings),
    path("public/site-content/", public_site_content),
    path("public/manual-payment/", submit_manual_payment),
    path("admin/account/", admin_account),
    path("admin/overview/", admin_overview),
    path("admin/orders/<int:pk>/approve/", approve_order),
    path("admin/orders/<int:pk>/reject/", reject_order),
    path("", include(router.urls)),
]

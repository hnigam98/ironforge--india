from django.contrib import admin
from .models import Profile, Coach, Plan, Program, NutritionTemplate, CoachRequest, Order, SiteSetting, CoachingSession, CoachReview

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user","role","plan_name","created_at")
    search_fields = ("user__username","user__email","user__first_name","user__last_name")
    list_filter = ("role",)

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("user","focus","active","hourly_rate","created_at")
    list_filter = ("active",)
    search_fields = ("user__username","user__email","focus")

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name","price","period","active")
    list_filter = ("active","period")

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name","goal","days_per_week","active")
    list_filter = ("active","goal")

@admin.register(NutritionTemplate)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ("name","diet_type","active")
    list_filter = ("active","diet_type")

@admin.register(CoachRequest)
class CoachRequestAdmin(admin.ModelAdmin):
    list_display = ("athlete","coach","need","status","created_at")
    list_filter = ("status","plan")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","user","plan","amount","status","utr","reviewed_by","created_at")
    list_filter = ("status",)
    search_fields = ("utr","razorpay_order_id","razorpay_payment_id","user__username","user__email")

    actions = ("approve_selected", "reject_selected")

    @admin.action(description="Approve selected UPI payments")
    def approve_selected(self, request, queryset):
        from django.utils import timezone
        for order in queryset.select_related("plan", "user"):
            order.status = "paid"
            order.reviewed_at = timezone.now()
            order.reviewed_by = request.user
            order.save(update_fields=["status", "reviewed_at", "reviewed_by"])
            profile, _ = Profile.objects.get_or_create(user=order.user)
            if order.plan:
                profile.plan_name = order.plan.name
                profile.save(update_fields=["plan_name"])

    @admin.action(description="Reject selected UPI payments")
    def reject_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="failed", reviewed_at=timezone.now(), reviewed_by=request.user)

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key","updated_at")


@admin.register(CoachingSession)
class CoachingSessionAdmin(admin.ModelAdmin):
    list_display=("athlete","coach","scheduled_at","status","created_at")
    list_filter=("status","coach")
    search_fields=("athlete__username","athlete__email","coach__user__username","topic")

@admin.register(CoachReview)
class CoachReviewAdmin(admin.ModelAdmin):
    list_display=("coach","athlete","rating","session","created_at")
    list_filter=("rating","coach")
    search_fields=("athlete__username","athlete__email","coach__user__username","review")
    readonly_fields=("session","athlete","coach","rating","review","created_at")

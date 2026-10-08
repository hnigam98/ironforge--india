from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = [
        ("athlete", "Athlete"),
        ("coach", "Coach"),
        ("admin", "Admin"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="athlete")
    phone = models.CharField(max_length=30, blank=True)
    bodyweight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    squat_1rm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    bench_1rm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    deadlift_1rm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    plan_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="coach")
    focus = models.CharField(max_length=160)
    tags = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True)
    initials = models.CharField(max_length=5, blank=True)
    active = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    whatsapp_number = models.CharField(max_length=30, blank=True, help_text="Coach WhatsApp number with country code, e.g. 919876543210")
    created_at = models.DateTimeField(auto_now_add=True)

class Plan(models.Model):
    PERIOD_CHOICES = [("month", "Month"), ("one-time", "One-time")]
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    features = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    razorpay_plan_id = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Program(models.Model):
    name = models.CharField(max_length=180)
    goal = models.CharField(max_length=100, default="Strength")
    days_per_week = models.PositiveSmallIntegerField(default=4)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class NutritionTemplate(models.Model):
    name = models.CharField(max_length=180)
    diet_type = models.CharField(max_length=80, default="General")
    target = models.CharField(max_length=180, default="Performance")
    content = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CoachRequest(models.Model):
    STATUS_CHOICES = [("pending","Pending"),("accepted","Accepted"),("rejected","Rejected"),("completed","Completed")]
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coach_requests")
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="requests")
    need = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES = [("created","Created"),("paid","Paid"),("failed","Failed"),("refunded","Refunded")]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="orders")
    customer_name = models.CharField(max_length=180, blank=True)
    customer_email = models.EmailField(blank=True)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    coach = models.ForeignKey(Coach, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    razorpay_order_id = models.CharField(max_length=120, blank=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    utr = models.CharField(max_length=120, blank=True, db_index=True)
    payment_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_orders")
    created_at = models.DateTimeField(auto_now_add=True)

class SiteSetting(models.Model):
    key = models.CharField(max_length=120, unique=True)
    value = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

class CoachingSession(models.Model):
    STATUS_CHOICES=[("scheduled","Scheduled"),("completed","Completed"),("cancelled","Cancelled"),("no_show","No Show")]
    athlete=models.ForeignKey(User,on_delete=models.CASCADE,related_name="coaching_sessions")
    coach=models.ForeignKey(Coach,on_delete=models.PROTECT,related_name="coaching_sessions")
    scheduled_at=models.DateTimeField()
    duration_minutes=models.PositiveSmallIntegerField(default=60)
    topic=models.CharField(max_length=200,blank=True)
    notes=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="scheduled")
    created_at=models.DateTimeField(auto_now_add=True)

class CoachReview(models.Model):
    session=models.OneToOneField(CoachingSession,on_delete=models.CASCADE,related_name="review")
    athlete=models.ForeignKey(User,on_delete=models.CASCADE,related_name="coach_reviews")
    coach=models.ForeignKey(Coach,on_delete=models.PROTECT,related_name="private_reviews")
    rating=models.PositiveSmallIntegerField()
    review=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=["-created_at"]

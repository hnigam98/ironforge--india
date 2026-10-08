from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, Coach, Plan, Program, NutritionTemplate, CoachRequest, Order, SiteSetting, CoachingSession, CoachReview
from .permissions import IsAdminUser, IsCoach
from .serializers import (
    UserSerializer, RegisterSerializer, ProfileSerializer, CoachSerializer,
    PlanSerializer, ProgramSerializer, NutritionTemplateSerializer,
    CoachRequestSerializer, OrderSerializer, SiteSettingSerializer, CoachingSessionSerializer, CoachReviewSerializer
)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

@api_view(["GET","PATCH"])
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return Response(ProfileSerializer(profile).data)
    s = ProfileSerializer(profile, data=request.data, partial=True)
    s.is_valid(raise_exception=True); s.save()
    return Response(s.data)

class PublicCoachViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CoachSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return Coach.objects.filter(active=True).select_related("user")

class PublicPlanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return Plan.objects.filter(active=True).order_by("price")

class ProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.all().order_by("-created_at")
    permission_classes = [IsAdminUser]

class NutritionViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionTemplateSerializer
    queryset = NutritionTemplate.objects.all().order_by("-created_at")
    permission_classes = [IsAdminUser]

class AdminCoachViewSet(viewsets.ModelViewSet):
    serializer_class = CoachSerializer
    queryset = Coach.objects.all().select_related("user").order_by("-created_at")
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        username = data.get("username") or data.get("email")
        email = data.get("email","")
        if not username:
            return Response({"detail":"username or email is required"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"detail":"username already exists"}, status=400)
        password = data.get("password") or get_random_string(16)
        user = User.objects.create_user(username=username, email=email, password=password, first_name=data.get("first_name",""), last_name=data.get("last_name",""))
        Profile.objects.create(user=user, role="coach")
        coach = Coach.objects.create(
            user=user, focus=data.get("focus","Powerlifting"), tags=data.get("tags",[]),
            bio=data.get("bio",""), initials=data.get("initials",""), active=data.get("active",True),
            hourly_rate=data.get("hourly_rate",0), whatsapp_number=data.get("whatsapp_number","")
        )
        return Response(CoachSerializer(coach).data, status=201)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        coach = self.get_object()
        data = request.data.copy()
        user = coach.user
        for field in ("email", "first_name", "last_name", "is_active"):
            if field in data:
                setattr(user, field, data.get(field))
        if data.get("password"):
            user.set_password(data.get("password"))
        user.save()
        for field in ("focus", "tags", "bio", "initials", "active", "hourly_rate", "whatsapp_number"):
            if field in data:
                setattr(coach, field, data.get(field))
        coach.save()
        return Response(CoachSerializer(coach).data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        coach = self.get_object()
        user = coach.user
        coach.delete()
        user.delete()
        return Response(status=204)

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all().order_by("price")
    permission_classes = [IsAdminUser]

class UserAdminViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [IsAdminUser]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().select_related("user","plan").order_by("-created_at")
        return Order.objects.filter(user=self.request.user).select_related("plan").order_by("-created_at")
    def perform_create(self, serializer):
        plan = get_object_or_404(Plan, pk=self.request.data.get("plan"))
        if not plan.active:
            raise ValidationError("Plan is not active")
        utr = str(self.request.data.get("utr", "")).strip()
        if not utr:
            raise ValidationError("UTR / transaction ID is required")
        coach = None
        if self.request.data.get("coach"):
            coach = get_object_or_404(Coach, pk=self.request.data.get("coach"), active=True)
        serializer.save(user=self.request.user, plan=plan, coach=coach, amount=plan.price, status="created", utr=utr, payment_note=str(self.request.data.get("payment_note", "")).strip())

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_overview(request):
    return Response({
        "users": User.objects.count(),
        "athletes": Profile.objects.filter(role="athlete").count(),
        "coaches": Coach.objects.count(),
        "active_coaches": Coach.objects.filter(active=True).count(),
        "plans": Plan.objects.count(),
        "active_plans": Plan.objects.filter(active=True).count(),
        "programs": Program.objects.count(),
        "nutrition": NutritionTemplate.objects.count(),
        "orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status="created").count(),
        "paid_orders": Order.objects.filter(status="paid").count(),
        "sessions": CoachingSession.objects.count(),
        "pending_reviews": CoachReview.objects.count(),
    })

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_site_content(request):
    setting = SiteSetting.objects.filter(key="site_content").first()
    return Response(setting.value if setting else {})

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_payment_settings(request):
    setting = SiteSetting.objects.filter(key="manual_payment").first()
    value = setting.value if setting else {}
    return Response(value)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def submit_manual_payment(request):
    """Guest-friendly UPI payment submission. No account is required."""
    name = str(request.data.get("name", "")).strip()
    email = str(request.data.get("email", "")).strip()
    utr = str(request.data.get("transaction_id", request.data.get("utr", ""))).strip()
    plan_id = request.data.get("plan")
    if not name or not email or not utr or not plan_id:
        return Response({"detail": "Name, email, plan and transaction ID are required."}, status=400)
    from django.core.validators import validate_email
    try:
        validate_email(email)
    except Exception:
        return Response({"detail": "Please enter a valid email address."}, status=400)
    plan = get_object_or_404(Plan, pk=plan_id, active=True)
    coach = None
    coach_id = request.data.get("coach")
    if coach_id:
        coach = get_object_or_404(Coach, pk=coach_id, active=True)
    order = Order.objects.create(
        user=None, customer_name=name, customer_email=email, plan=plan, coach=coach,
        amount=plan.price, currency="INR", status="created", utr=utr,
        payment_note="Guest payment submission"
    )
    return Response({
        "message": "Payment details submitted. Your payment is pending admin verification.",
        "payment_id": order.id, "status": order.status, "plan": plan.name, "amount": str(plan.price),
        "coach": coach.id if coach else None, "coach_name": coach.user.get_full_name() if coach else "",
        "coach_whatsapp_url": ("https://wa.me/" + "".join(ch for ch in coach.whatsapp_number if ch.isdigit())) if coach and coach.whatsapp_number else ""
    }, status=201)

@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def admin_account(request):
    """Allow the currently logged-in admin to change their own username/email/password."""
    user = request.user
    username = str(request.data.get("username", user.username)).strip()
    email = str(request.data.get("email", user.email)).strip()
    password = request.data.get("password")
    if not username:
        return Response({"detail": "Username cannot be empty."}, status=400)
    if User.objects.filter(username=username).exclude(pk=user.pk).exists():
        return Response({"detail": "That username is already in use."}, status=400)
    user.username = username
    user.email = email
    if password:
        if len(password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=400)
        user.set_password(password)
    user.save()
    return Response({"message": "Admin account updated. If you changed the password, log in again.", "username": user.username, "email": user.email})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == "paid":
        return Response({"detail": "Order is already approved.", "order": OrderSerializer(order).data})
    order.status = "paid"
    order.reviewed_at = timezone.now()
    order.reviewed_by = request.user
    order.save(update_fields=["status", "reviewed_at", "reviewed_by"])
    if order.user and order.plan:
        profile, _ = Profile.objects.get_or_create(user=order.user)
        profile.plan_name = order.plan.name
        profile.save(update_fields=["plan_name"])
    message = "Payment approved." if not order.user else "Payment approved and plan activated."
    data = {"detail": message, "order": OrderSerializer(order).data}
    if order.coach and order.coach.whatsapp_number:
        import urllib.parse
        client = order.customer_name or (order.user.get_full_name() if order.user else "Client")
        email = order.customer_email or (order.user.email if order.user else "")
        text = f"""Hello {order.coach.user.get_full_name() or order.coach.user.username}, a new IRONFORGE client has completed payment.

Client: {client}
Email: {email}
Plan: {order.plan.name if order.plan else "-"}
Amount: ₹{order.amount}
UTR: {order.utr}

Please contact the client for coaching/session arrangements."""
        data["coach_whatsapp_url"] = "https://wa.me/" + "".join(ch for ch in order.coach.whatsapp_number if ch.isdigit()) + "?text=" + urllib.parse.quote(text)
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def reject_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = "failed"
    order.reviewed_at = timezone.now()
    order.reviewed_by = request.user
    order.save(update_fields=["status", "reviewed_at", "reviewed_by"])
    return Response({"detail": "Payment rejected.", "order": OrderSerializer(order).data})

class CoachRequestViewSet(viewsets.ModelViewSet):
    serializer_class = CoachRequestSerializer
    def get_queryset(self):
        if self.request.user.is_staff:
            return CoachRequest.objects.all().select_related("athlete","coach__user")
        if hasattr(self.request.user, "coach"):
            return CoachRequest.objects.filter(coach=self.request.user.coach).select_related("athlete","coach__user")
        return CoachRequest.objects.filter(athlete=self.request.user).select_related("athlete","coach__user")
    def perform_create(self, serializer):
        serializer.save(athlete=self.request.user)

class AdminSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSettingSerializer
    queryset = SiteSetting.objects.all().order_by("key")
    permission_classes = [IsAdminUser]


class CoachingSessionViewSet(viewsets.ModelViewSet):
    serializer_class=CoachingSessionSerializer
    def get_queryset(self):
        u=self.request.user
        if u.is_staff: return CoachingSession.objects.all().select_related("athlete","coach__user").order_by("-scheduled_at")
        if hasattr(u,"coach"): return CoachingSession.objects.filter(coach=u.coach).select_related("athlete","coach__user").order_by("-scheduled_at")
        return CoachingSession.objects.filter(athlete=u).select_related("athlete","coach__user").order_by("-scheduled_at")
    def perform_create(self,serializer):
        u=self.request.user
        if u.is_staff: serializer.save()
        elif hasattr(u,"coach") and u.coach.active: serializer.save(coach=u.coach,athlete_id=self.request.data.get("athlete"))
        else:
            coach = get_object_or_404(Coach, pk=self.request.data.get("coach"), active=True)
            if not Order.objects.filter(user=u, status="paid", coach=coach).exists():
                raise permissions.PermissionDenied("A verified paid coaching plan with this coach is required before booking a session.")
            serializer.save(coach=coach, athlete=u)
    def perform_update(self,serializer):
        u=self.request.user; obj=self.get_object()
        if u.is_staff or (hasattr(u,"coach") and obj.coach_id==u.coach.id): serializer.save()
        else: raise permissions.PermissionDenied("You can only manage your own coaching sessions.")

class PrivateCoachReviewViewSet(viewsets.ModelViewSet):
    serializer_class=CoachReviewSerializer
    def get_queryset(self):
        if not self.request.user.is_staff: return CoachReview.objects.none()
        return CoachReview.objects.all().select_related("athlete","coach__user","session")
    def create(self,request,*args,**kwargs):
        if request.user.is_staff or hasattr(request.user,"coach"):
            raise permissions.PermissionDenied("Reviews are submitted by athletes only and are private from coaches.")
        session=get_object_or_404(CoachingSession,pk=request.data.get("session"),athlete=request.user)
        if session.status!="completed": return Response({"detail":"Review is available only after a completed session."},status=400)
        if CoachReview.objects.filter(session=session).exists(): return Response({"detail":"Review already submitted."},status=400)
        rating=int(request.data.get("rating",0))
        if rating<1 or rating>5: return Response({"detail":"Rating must be between 1 and 5."},status=400)
        r=CoachReview.objects.create(session=session,athlete=request.user,coach=session.coach,rating=rating,review=request.data.get("review",""))
        return Response(CoachReviewSerializer(r).data,status=201)

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Coach, Plan, Program, NutritionTemplate, CoachRequest, Order, SiteSetting, CoachingSession, CoachReview

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    class Meta:
        model = User
        fields = ["id","username","email","first_name","last_name","role","is_staff","is_active","date_joined","password"]
        read_only_fields = ["id","username","role","is_staff","date_joined"]
    def get_role(self, obj):
        return getattr(getattr(obj, "profile", None), "role", "athlete")
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    def create(self, validated):
        user = User.objects.create_user(
            username=validated["username"], email=validated["email"],
            password=validated["password"], first_name=validated.get("first_name",""),
            last_name=validated.get("last_name","")
        )
        Profile.objects.create(user=user, role="athlete")
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user","created_at"]

class CoachSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Coach
        fields = "__all__"
        read_only_fields = ["created_at"]

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        read_only_fields = ["created_at"]

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"
        read_only_fields = ["created_at"]

class NutritionTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionTemplate
        fields = "__all__"
        read_only_fields = ["created_at"]

class CoachRequestSerializer(serializers.ModelSerializer):
    athlete = UserSerializer(read_only=True)
    class Meta:
        model = CoachRequest
        fields = "__all__"
        read_only_fields = ["athlete","created_at"]

class OrderSerializer(serializers.ModelSerializer):
    coach_name = serializers.CharField(source="coach.user.get_full_name", read_only=True)
    coach_whatsapp = serializers.CharField(source="coach.whatsapp_number", read_only=True)
    coach_whatsapp_url = serializers.SerializerMethodField()
    def get_coach_whatsapp_url(self, obj):
        if not obj.coach or not obj.coach.whatsapp_number:
            return ""
        return "https://wa.me/" + "".join(ch for ch in obj.coach.whatsapp_number if ch.isdigit())
    class Meta:
        model = Order
        fields = ["id","user","customer_name","customer_email","plan","coach","amount","currency","status","razorpay_order_id","razorpay_payment_id","razorpay_signature","utr","payment_note","reviewed_at","reviewed_by","created_at","coach_name","coach_whatsapp","coach_whatsapp_url"]
        read_only_fields = ["user","status","amount","currency","razorpay_order_id","razorpay_payment_id","razorpay_signature","reviewed_at","reviewed_by","created_at"]

class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = "__all__"


class CoachingSessionSerializer(serializers.ModelSerializer):
    coach_name=serializers.CharField(source="coach.user.get_full_name",read_only=True)
    athlete_name=serializers.CharField(source="athlete.get_full_name",read_only=True)
    coach_whatsapp=serializers.CharField(source="coach.whatsapp_number",read_only=True)
    coach_whatsapp_url=serializers.SerializerMethodField()
    def get_coach_whatsapp_url(self,obj):
        if not obj.coach or not obj.coach.whatsapp_number: return ""
        return "https://wa.me/" + "".join(ch for ch in obj.coach.whatsapp_number if ch.isdigit())
    class Meta:
        model=CoachingSession
        fields=["id","athlete","coach","scheduled_at","duration_minutes","topic","notes","status","created_at","coach_whatsapp","coach_whatsapp_url"]
        read_only_fields=["created_at"]

class CoachReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=CoachReview
        fields=["id","session","athlete","coach","rating","review","created_at"]
        read_only_fields=["athlete","coach","created_at"]

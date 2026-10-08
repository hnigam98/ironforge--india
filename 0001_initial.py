from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_manual_payment(apps, schema_editor):
    SiteSetting = apps.get_model('api', 'SiteSetting')
    SiteSetting.objects.update_or_create(
        key='manual_payment',
        defaults={'value': {
            'enabled': True,
            'upi_id': 'nigamhimanshu80-2@oksbi',
            'account_name': 'Himanshu Nigam',
            'qr_image_url': '/static/assets/himanshu_upi_qr.jpg',
            'instructions': 'Pay the exact amount, then enter the UTR/transaction ID. Your plan will be activated after admin verification.'
        }}
    )
    Plan = apps.get_model('api', 'Plan')
    plans = [
        ('Beginner', 299, 'month'), ('Intermediate', 599, 'month'), ('Advanced', 999, 'month'),
        ('PRO', 1299, 'month'), ('Elite', 1499, 'month'), ('Diet Only', 199, 'one-time'),
        ('Workout Only', 299, 'one-time'), ('Workout + Diet', 499, 'one-time')
    ]
    for name, price, period in plans:
        Plan.objects.update_or_create(name=name, defaults={'price': price, 'period': period, 'active': True})

class Migration(migrations.Migration):
    initial = True
    dependencies = [('auth', '0012_alter_user_first_name_max_length')]
    operations = [
        migrations.CreateModel(name='Profile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('role', models.CharField(choices=[('athlete','Athlete'),('coach','Coach'),('admin','Admin')], default='athlete', max_length=20)),
            ('phone', models.CharField(blank=True, max_length=30)),
            ('bodyweight', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ('height_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ('squat_1rm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
            ('bench_1rm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
            ('deadlift_1rm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
            ('plan_name', models.CharField(blank=True, max_length=120)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Coach', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('focus', models.CharField(max_length=160)), ('tags', models.JSONField(blank=True, default=list)),
            ('bio', models.TextField(blank=True)), ('initials', models.CharField(blank=True, max_length=5)),
            ('active', models.BooleanField(default=True)), ('hourly_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coach', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Plan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=120, unique=True)), ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ('period', models.CharField(choices=[('month','Month'),('one-time','One-time')], max_length=20)),
            ('features', models.JSONField(blank=True, default=list)), ('active', models.BooleanField(default=True)),
            ('razorpay_plan_id', models.CharField(blank=True, max_length=120)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='Program', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=180)), ('goal', models.CharField(default='Strength', max_length=100)),
            ('days_per_week', models.PositiveSmallIntegerField(default=4)), ('description', models.TextField(blank=True)),
            ('active', models.BooleanField(default=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='NutritionTemplate', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=180)), ('diet_type', models.CharField(default='General', max_length=80)),
            ('target', models.CharField(default='Performance', max_length=180)), ('content', models.JSONField(blank=True, default=dict)),
            ('active', models.BooleanField(default=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='CoachRequest', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('need', models.CharField(max_length=160)), ('message', models.TextField(blank=True)),
            ('status', models.CharField(choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected'),('completed','Completed')], default='pending', max_length=20)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coach_requests', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='SiteSetting', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('key', models.CharField(max_length=120, unique=True)), ('value', models.JSONField(default=dict)), ('updated_at', models.DateTimeField(auto_now=True)),
        ]),
        migrations.CreateModel(name='Order', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('amount', models.DecimalField(decimal_places=2, max_digits=10)), ('currency', models.CharField(default='INR', max_length=10)),
            ('status', models.CharField(choices=[('created','Created'),('paid','Paid'),('failed','Failed'),('refunded','Refunded')], default='created', max_length=20)),
            ('razorpay_order_id', models.CharField(blank=True, db_index=True, max_length=120)), ('razorpay_payment_id', models.CharField(blank=True, max_length=120)),
            ('razorpay_signature', models.CharField(blank=True, max_length=255)), ('utr', models.CharField(blank=True, db_index=True, max_length=120)),
            ('payment_note', models.TextField(blank=True)), ('reviewed_at', models.DateTimeField(blank=True, null=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.plan')),
            ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_orders', to=settings.AUTH_USER_MODEL)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='CoachingSession', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('scheduled_at', models.DateTimeField()), ('duration_minutes', models.PositiveSmallIntegerField(default=60)),
            ('topic', models.CharField(blank=True, max_length=200)), ('notes', models.TextField(blank=True)),
            ('status', models.CharField(choices=[('scheduled','Scheduled'),('completed','Completed'),('cancelled','Cancelled'),('no_show','No Show')], default='scheduled', max_length=20)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_sessions', to=settings.AUTH_USER_MODEL)),
            ('coach', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coaching_sessions', to='api.coach')),
        ]),
        migrations.CreateModel(name='CoachReview', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('rating', models.PositiveSmallIntegerField()), ('review', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coach_reviews', to=settings.AUTH_USER_MODEL)),
            ('coach', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='private_reviews', to='api.coach')),
            ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='api.coachingsession')),
        ], options={'ordering':['-created_at']}),
        migrations.AddField(model_name='coachrequest', name='coach', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.coach')),
        migrations.RunPython(seed_manual_payment, migrations.RunPython.noop),
    ]

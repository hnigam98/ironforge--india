from django.db import migrations, models
import django.db.models.deletion

def seed_site_content(apps, schema_editor):
    SiteSetting = apps.get_model('api', 'SiteSetting')
    SiteSetting.objects.update_or_create(
        key='site_content',
        defaults={'value': {
            'announcement': 'Engineered for Indian Strength Athletes',
            'heroTitle': 'Everything a lifter needs. One IronForge.',
            'heroDescription': 'Training, Indian nutrition, personal coaching support, form feedback and competition preparation in one responsive platform.',
            'earlyAccess': '',
            'footer': 'IRONFORGE INDIA • Built for strength athletes • One-time plans do not create permanent profiles.',
            'features': [
                {'icon': '🏋️', 'title': 'Adaptive Training', 'description': 'Sessions built around strength numbers, RPE, fatigue and progression.', 'active': True},
                {'icon': '🍛', 'title': 'Desi Nutrition', 'description': 'Practical Indian meals, food swaps and budget-aware planning.', 'active': True},
                {'icon': '🎥', 'title': 'Technique Review', 'description': 'Focused squat, bench and deadlift technique guidance.', 'active': True},
                {'icon': '💬', 'title': 'Coach Assistant', 'description': 'Practical answers for training, nutrition, recovery and competition.', 'active': True},
                {'icon': '🏆', 'title': 'Meet Preparation', 'description': 'Warm-ups, attempts, timing and meet-day decisions.', 'active': True},
                {'icon': '📊', 'title': 'Lifter Dashboard', 'description': 'Keep profile, training, nutrition and competition work together.', 'active': True},
            ]
        }}
    )

class Migration(migrations.Migration):
    dependencies = [("api", "0002_set_himanshu_upi")]
    operations = [
        migrations.AlterField(
            model_name="order", name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="auth.user"),
        ),
        migrations.AddField(model_name="order", name="customer_name", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="order", name="customer_email", field=models.EmailField(blank=True, max_length=254)),
        migrations.RunPython(seed_site_content, migrations.RunPython.noop),
    ]

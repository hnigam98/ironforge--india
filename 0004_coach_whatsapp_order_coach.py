from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("api", "0003_guest_payments_admin_account")]
    operations = [
        migrations.AddField(model_name="coach", name="whatsapp_number", field=models.CharField(blank=True, help_text="Coach WhatsApp number with country code, e.g. 919876543210", max_length=30)),
        migrations.AddField(model_name="order", name="coach", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="api.coach")),
    ]

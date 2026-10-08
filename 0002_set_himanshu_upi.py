from django.db import migrations

def set_himanshu_upi(apps, schema_editor):
    SiteSetting = apps.get_model("api", "SiteSetting")
    SiteSetting.objects.update_or_create(
        key="manual_payment",
        defaults={"value": {
            "enabled": True,
            "upi_id": "nigamhimanshu80-2@oksbi",
            "account_name": "Himanshu Nigam",
            "qr_image_url": "/static/assets/himanshu_upi_qr.jpg",
            "instructions": "Pay the exact amount, then enter the UTR / transaction ID. Your plan is activated after admin verification."
        }}
    )

class Migration(migrations.Migration):
    dependencies = [("api", "0001_initial")]
    operations = [migrations.RunPython(set_himanshu_upi, migrations.RunPython.noop)]

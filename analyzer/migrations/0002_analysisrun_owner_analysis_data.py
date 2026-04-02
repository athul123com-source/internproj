from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("analyzer", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="analysisrun",
            name="analysis_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="analysisrun",
            name="owner",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="analysis_runs", to=settings.AUTH_USER_MODEL),
        ),
    ]

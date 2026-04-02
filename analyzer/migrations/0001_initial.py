from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnalysisRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("role", models.CharField(max_length=120)),
                ("filename", models.CharField(max_length=255)),
                ("resume_score", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

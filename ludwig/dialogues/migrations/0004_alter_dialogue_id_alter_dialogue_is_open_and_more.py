# Generated by Django 5.2 on 2025-05-03 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dialogues", "0003_alter_dialogue_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dialogue",
            name="id",
            field=models.CharField(
                default="vslviqbev3",
                editable=False,
                max_length=10,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="dialogue",
            name="is_open",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="dialogue",
            name="is_visible",
            field=models.BooleanField(default=True),
        ),
    ]

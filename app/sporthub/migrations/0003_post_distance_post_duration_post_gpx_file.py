# Generated by Django 5.0.4 on 2024-05-02 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sporthub', '0002_post_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='distance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='gpx_file',
            field=models.FileField(blank=True, null=True, upload_to='gpx_files'),
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-25 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parrainage_backend', '0005_objectifparrains'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parrainages_requis', models.PositiveIntegerField(default=50000)),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='ObjectifParrains',
        ),
    ]

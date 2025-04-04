# Generated by Django 5.1.7 on 2025-03-22 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parrainage_backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoriqueImportation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=255)),
                ('user_prenom', models.CharField(max_length=255)),
                ('user_ip', models.GenericIPAddressField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
            ],
        ),
    ]

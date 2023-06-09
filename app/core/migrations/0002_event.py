# Generated by Django 4.1.7 on 2023-04-02 02:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('location', models.CharField(max_length=128)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('attenders', models.ManyToManyField(related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

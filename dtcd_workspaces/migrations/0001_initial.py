# Generated by Django 3.2.9 on 2023-06-21 10:15

from django.db import migrations, models
import rest_auth.models.abc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DirectoryContentKeychain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('_zone', models.IntegerField(blank=True, null=True)),
                ('_auth_objects', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
            bases=(rest_auth.models.abc.IKeyChain, models.Model),
        ),
    ]

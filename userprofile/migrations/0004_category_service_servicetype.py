# Generated by Django 3.1.6 on 2021-03-01 08:38

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0003_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('Remotely', 'Удаленно'), ("Student's home", 'У ученика'), ("Tutor's home", 'У преподавателя'), ('Any', 'Любое')], default='Any', max_length=200), size=None)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('price', models.IntegerField()),
                ('isTutor', models.BooleanField()),
                ('isActive', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_list', to='userprofile.category')),
                ('types', models.ManyToManyField(to='userprofile.ServiceType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

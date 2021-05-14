# Generated by Django 3.2 on 2021-05-14 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ROI', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('accuracy', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('fights_analyzed', models.IntegerField(default=0)),
            ],
        ),
    ]

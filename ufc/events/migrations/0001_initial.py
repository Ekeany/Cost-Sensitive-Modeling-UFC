# Generated by Django 3.2 on 2021-05-13 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('future', models.BooleanField(default=True)),
                ('event_name', models.CharField(blank='False', max_length=255)),
                ('expected_returns', models.IntegerField(blank='False', default=0)),
                ('num_fights_predicted', models.IntegerField(blank='False', default=0)),
                ('num_total_fights', models.IntegerField(blank='False', default=0)),
                ('ROI', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('accuracy', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('event_date', models.DateField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
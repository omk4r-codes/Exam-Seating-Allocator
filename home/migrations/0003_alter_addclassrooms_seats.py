# Generated by Django 5.0.4 on 2024-04-05 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_addclassrooms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addclassrooms',
            name='seats',
            field=models.IntegerField(),
        ),
    ]
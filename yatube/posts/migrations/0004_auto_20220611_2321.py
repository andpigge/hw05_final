# Generated by Django 2.2.9 on 2022-06-11 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20220611_2310'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date_edit']},
        ),
        migrations.AddField(
            model_name='post',
            name='post_edit',
            field=models.BooleanField(default=False),
        ),
    ]

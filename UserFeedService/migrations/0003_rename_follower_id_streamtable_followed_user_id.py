# Generated by Django 4.2.3 on 2023-07-28 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserFeedService', '0002_streamtable_follower_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='streamtable',
            old_name='follower_id',
            new_name='followed_user_id',
        ),
    ]
# Generated by Django 3.2.3 on 2023-07-03 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_following_followinguser'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FollowingUser',
            new_name='FollowingAuthor',
        ),
    ]
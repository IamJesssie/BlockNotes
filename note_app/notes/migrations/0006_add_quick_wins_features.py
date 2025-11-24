# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0005_set_tags_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='note',
            name='pinned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='note',
            name='archived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='note',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='color',
            field=models.CharField(blank=True, default='default', max_length=20),
        ),
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ['-is_pinned', '-updated_at']},
        ),
    ]

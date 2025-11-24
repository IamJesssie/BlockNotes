from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('notes', '0004_drop_extra_columns'),
    ]

    operations = [
        # Update NULL tags to empty string
        migrations.RunSQL(
            sql="UPDATE notes_note SET tags = '' WHERE tags IS NULL",
            reverse_sql=migrations.RunSQL.noop
        ),
        # Alter tags column to have default value
        migrations.RunSQL(
            sql="ALTER TABLE notes_note MODIFY COLUMN tags VARCHAR(255) NOT NULL DEFAULT ''",
            reverse_sql=migrations.RunSQL.noop
        ),
    ]

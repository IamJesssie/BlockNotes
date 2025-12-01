from django.db import migrations
from django.db import connection

def drop_extra_columns(apps, schema_editor):
    # Only run this on MySQL
    if connection.vendor == 'mysql':
        with connection.cursor() as cursor:
            columns = ['color', 'is_archived', 'is_deleted', 'is_pinned', 'archived_at', 'deleted_at', 'pinned_at']
            for col in columns:
                # Check if column exists before dropping
                cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='{col}' AND table_schema=DATABASE()")
                if cursor.fetchone()[0] > 0:
                    cursor.execute(f"ALTER TABLE notes_note DROP COLUMN {col}")

class Migration(migrations.Migration):
    """
    Drop columns that were manually added to the database.
    This script removes: color, is_archived, is_deleted, is_pinned, 
    archived_at, deleted_at, pinned_at
    """

    atomic = False

    dependencies = [
        ('notes', '0003_alter_blockchainreceipt_options_and_more'),
    ]

    operations = [
        migrations.RunPython(drop_extra_columns, reverse_code=migrations.RunPython.noop),
    ]


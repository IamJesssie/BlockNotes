from django.db import migrations


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
        # Drop each column separately - MySQL doesn't support multiple IF EXISTS in one ALTER
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='color' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN color', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='is_archived' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN is_archived', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='is_deleted' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN is_deleted', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='is_pinned' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN is_pinned', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='archived_at' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN archived_at', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='deleted_at' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN deleted_at', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql="SET @drop_col = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='notes_note' AND column_name='pinned_at' AND table_schema=DATABASE()) > 0, 'ALTER TABLE notes_note DROP COLUMN pinned_at', 'SELECT 1'); PREPARE stmt FROM @drop_col; EXECUTE stmt;",
            reverse_sql=migrations.RunSQL.noop
        ),
    ]


from django.db import migrations


def update_charset(apps, schema_editor):
    """Update database tables and columns to use utf8mb4 charset for emoji support."""
    # Only apply for MySQL backend
    if schema_editor.connection.vendor != 'mysql':
        return
    
    # Update database charset
    schema_editor.execute("ALTER DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    # Update chat_conversations table
    schema_editor.execute("ALTER TABLE chat_conversations CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    # Update chat_messages table
    schema_editor.execute("ALTER TABLE chat_messages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    # Specifically update text columns that might store emoji content
    schema_editor.execute("""
        ALTER TABLE chat_messages 
        MODIFY content_markdown TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        MODIFY content_text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)
    
    schema_editor.execute("""
        ALTER TABLE chat_conversations 
        MODIFY title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        MODIFY system_prompt TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """)


def reverse_charset(apps, schema_editor):
    """Reverse charset update (optional, for rollback)."""
    # Only apply for MySQL backend
    if schema_editor.connection.vendor != 'mysql':
        return
    
    # Revert to utf8 (not recommended for production)
    schema_editor.execute("ALTER DATABASE CHARACTER SET utf8 COLLATE utf8_general_ci;")
    schema_editor.execute("ALTER TABLE chat_conversations CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;")
    schema_editor.execute("ALTER TABLE chat_messages CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;")


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_charset, reverse_charset),
    ]

from django.db import migrations


def update_charset(apps, schema_editor):
    """仅更新聊天相关表和列的字符集为 utf8mb4，不修改整库默认字符集。"""
    if schema_editor.connection.vendor != 'mysql':
        return

    schema_editor.execute(
        "ALTER TABLE chat_conversations CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    schema_editor.execute(
        "ALTER TABLE chat_messages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )

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
    """回滚聊天相关表的字符集（仅用于开发回滚，不推荐生产环境执行）。"""
    if schema_editor.connection.vendor != 'mysql':
        return

    schema_editor.execute(
        "ALTER TABLE chat_conversations CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;"
    )
    schema_editor.execute(
        "ALTER TABLE chat_messages CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;"
    )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_charset, reverse_charset, atomic=False),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Conversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(blank=True, default="", max_length=255)),
                ("title_source", models.CharField(choices=[("auto", "Auto"), ("manual", "Manual")], default="auto", max_length=20)),
                ("model_code", models.CharField(default="deepseek-chat", max_length=50)),
                ("system_prompt", models.TextField(blank=True, default="")),
                ("last_message_at", models.DateTimeField(blank=True, null=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_conversations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "chat_conversations",
                "ordering": ["-last_message_at", "-updated_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("role", models.CharField(choices=[("user", "User"), ("assistant", "Assistant"), ("system", "System")], max_length=20)),
                ("content_markdown", models.TextField(blank=True, default="")),
                ("content_text", models.TextField(blank=True, default="")),
                ("status", models.CharField(choices=[("completed", "Completed"), ("streaming", "Streaming"), ("stopped", "Stopped"), ("failed", "Failed")], default="completed", max_length=20)),
                ("sequence_no", models.IntegerField()),
                ("provider_message_id", models.CharField(blank=True, default="", max_length=100)),
                ("error_code", models.CharField(blank=True, default="", max_length=50)),
                ("error_message", models.CharField(blank=True, default="", max_length=255)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="chat.conversation")),
                ("regen_from_message", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="regen_children", to="chat.message")),
                ("reply_to_message", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assistant_replies", to="chat.message")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "chat_messages",
                "ordering": ["sequence_no", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(fields=["user", "-last_message_at"], name="chat_conv_user_last_msg_idx"),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(fields=["user", "deleted_at"], name="chat_conv_user_deleted_idx"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["conversation", "sequence_no"], name="chat_msg_conv_seq_idx"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["conversation", "created_at"], name="chat_msg_conv_created_idx"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["user", "conversation"], name="chat_msg_user_conv_idx"),
        ),
        migrations.AddConstraint(
            model_name="message",
            constraint=models.UniqueConstraint(fields=("conversation", "sequence_no"), name="chat_msg_unique_sequence"),
        ),
    ]
